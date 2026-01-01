import asyncio
import datetime
import logging
from typing import List

import requests
import uvicorn
from bs4 import BeautifulSoup
from environs import env
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .utils import now, unwrap

BUS_STOP_REF = env.str("BUS_STOP_REF")
TRAIN_QUERY = env.str("TRAIN_QUERY")
TRAIN_API_KEY = env.str("TRAIN_API_KEY")
CACHE_TTL_SECONDS = env.int("CACHE_TTL_SECONDS", 30)

TRAIN_SERVICE_TYPES = {
    "bus": "BUS",
    "ferry": "FRY",
    "train": "TRN",
    "unknown": "UNK",
}


class TransitRow(BaseModel):
    eta: str
    service: str
    dest: str


class TransitInfo(BaseModel):
    title: str
    departures: List[TransitRow] = Field(default=[])


class AllTransitInfo(BaseModel):
    time: int = Field(default_factory=lambda: now())
    bus_info: TransitInfo = Field(
        default=TransitInfo(title="Buses", departures=[])
    )
    train_info: TransitInfo = Field(
        default=TransitInfo(title="Trains", departures=[])
    )


def fetch_bus_info() -> TransitInfo:
    url = f"https://www.cambridgeshirebus.info/Popup_Content/WebDisplay/WebDisplay.aspx?stopRef={BUS_STOP_REF}"
    r = requests.get(url, timeout=(3, 10))
    result = TransitInfo(title="Buses", departures=[])

    if not r.ok:
        logging.error(f"Failed to GET bus info: {r.status_code}")
        return result

    try:
        soup = BeautifulSoup(r.text, features="html.parser")
        # unsafe unwrapping of Optional values but fine for now
        table = unwrap(soup.select_one(".rtiTable"))

        station_name = (
            unwrap(soup.select_one("#stopTitle"))
            .get_text()
            .split("-")[0]
            .strip()
        )
        result.title = f"Buses - {station_name}"

        for row in table.select(".gridRow"):
            service = unwrap(row.select_one(".gridServiceItem")).get_text()
            dest = unwrap(row.select_one(".gridDestinationItem")).get_text()
            eta = unwrap(row.select_one(".gridTimeItem")).get_text()
            result.departures.append(
                TransitRow(eta=eta, service=service, dest=dest)
            )
    except Exception as e:
        logging.error(f"Error parsing bus info: {e}")

    return result


def fetch_train_info() -> TransitInfo:
    url = f"https://api1.raildata.org.uk/1010-live-departure-board-dep1_2/LDBWS/api/20220120/GetDepartureBoard/{TRAIN_QUERY}"
    r = requests.get(
        url,
        headers={"x-apikey": TRAIN_API_KEY, "User-Agent": ""},
        timeout=(3, 10),
    )
    result = TransitInfo(title="Trains", departures=[])
    if not r.ok:
        logging.error(f"Failed to fetch train info: {r.status_code}")
        return result

    data = r.json()
    departures = [
        *data.get("trainServices", []),
        *data.get("busServices", []),
    ]
    departures.sort(key=lambda s: datetime.time.fromisoformat(s.get("std")))

    station_name = data.get("locationName", "Unknown Station")
    result.title = f"Trains - {station_name}"

    for service in departures:
        std = service.get("std")
        etd = service.get("etd", "On time")
        eta = f"{std} ({etd})" if etd != "On time" else std
        dest = service.get("destination", [{}])[-1].get(
            "locationName", "Unknown"
        )
        service_name = TRAIN_SERVICE_TYPES.get(
            service.get("serviceType", "unknown"),
            TRAIN_SERVICE_TYPES["unknown"],
        )
        result.departures.append(
            TransitRow(eta=eta, service=service_name, dest=dest)
        )

    return result


def is_cache_fresh() -> bool:
    return (now() - cache.time) < CACHE_TTL_SECONDS


app = FastAPI()
cache = AllTransitInfo()
cache_lock = asyncio.Lock()


@app.get("/")
async def get_root() -> AllTransitInfo:
    global cache, cache_lock

    if (now() - cache.time) < CACHE_TTL_SECONDS:
        return cache

    async with cache_lock:
        if is_cache_fresh():
            return cache
        cache = AllTransitInfo(
            bus_info=fetch_bus_info(), train_info=fetch_train_info()
        )
        return cache


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
