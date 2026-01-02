import asyncio
import logging
from datetime import datetime, time
from typing import List

import aiohttp
import uvicorn
from async_lru import alru_cache
from bs4 import BeautifulSoup
from environs import env
from fastapi import FastAPI
from pydantic import BaseModel, Field

BUS_STOP_REF = env.str("BUS_STOP_REF")
TRAIN_QUERY = env.str("TRAIN_QUERY")
TRAIN_API_KEY = env.str("TRAIN_API_KEY")
CACHE_TTL_SECONDS = env.int("CACHE_TTL_SECONDS", 30)
CLIENT_TIMEOUT_SECONDS = env.int("CLIENT_TIMEOUT_SECONDS", 10)

TRAIN_SERVICE_TYPES = {
    "bus": "BUS",
    "ferry": "FRY",
    "train": "TRN",
    "unknown": "UNK",
}

app = FastAPI()


class TransitRow(BaseModel):
    eta: str
    service: str
    dest: str


class TransitInfo(BaseModel):
    title: str
    departures: List[TransitRow] = Field(default_factory=list)


class AllTransitInfo(BaseModel):
    time: int
    bus_info: TransitInfo
    train_info: TransitInfo


def unwrap[T](v: T | None) -> T:
    assert v is not None
    return v


async def fetch_bus_info(session: aiohttp.ClientSession) -> TransitInfo:
    url = f"https://www.cambridgeshirebus.info/Popup_Content/WebDisplay/WebDisplay.aspx?stopRef={BUS_STOP_REF}"
    try:
        async with session.get(url) as r:
            if not r.ok:
                logging.error(f"Failed to fetch bus info: {r.status}")
                return TransitInfo(
                    title=f"Buses - Failed to fetch: {r.status}"
                )

            text = await r.text()
            soup = BeautifulSoup(text, features="html.parser")
            table = unwrap(soup.select_one(".rtiTable"))
            station_name = (
                unwrap(soup.select_one("#stopTitle"))
                .get_text()
                .split("-")[0]
                .strip()
            )
            result = TransitInfo(title=f"Buses - {station_name}")
            for row in table.select(".gridRow"):
                service = unwrap(row.select_one(".gridServiceItem")).get_text()
                dest = unwrap(
                    row.select_one(".gridDestinationItem")
                ).get_text()
                eta = unwrap(row.select_one(".gridTimeItem")).get_text()
                result.departures.append(
                    TransitRow(eta=eta, service=service, dest=dest)
                )

            return result
    except Exception as e:
        logging.exception(f"Exception while fetching bus info: {e}")
        return TransitInfo(title="Buses - Exception occurred")


async def fetch_train_info(session: aiohttp.ClientSession) -> TransitInfo:
    url = f"https://api1.raildata.org.uk/1010-live-departure-board-dep1_2/LDBWS/api/20220120/GetDepartureBoard/{TRAIN_QUERY}"
    headers = {"x-apikey": TRAIN_API_KEY, "User-Agent": ""}
    try:
        async with session.get(url, headers=headers) as r:
            if not r.ok:
                logging.error(f"Failed to fetch train info: {r.status}")
                return TransitInfo(
                    title=f"Trains - Failed to fetch: {r.status}"
                )

            data = await r.json()
            departures = [
                *data.get("trainServices", []),
                *data.get("busServices", []),
            ]
            # TODO make resilient to missing/invalid std values
            departures.sort(key=lambda s: time.fromisoformat(s.get("std")))

            station_name = data.get("locationName", "Unknown Station")
            result = TransitInfo(title=f"Trains - {station_name}")

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
    except Exception as e:
        logging.exception(f"Exception while fetching train info: {e}")
        return TransitInfo(title="Trains - Exception occurred")


@alru_cache(maxsize=1, ttl=CACHE_TTL_SECONDS)
async def fetch_all_info() -> AllTransitInfo:
    timeout = aiohttp.ClientTimeout(total=CLIENT_TIMEOUT_SECONDS)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        bus_info, train_info = await asyncio.gather(
            fetch_bus_info(session),
            fetch_train_info(session),
        )
        time = int(datetime.now().timestamp())
        return AllTransitInfo(
            bus_info=bus_info,
            train_info=train_info,
            time=time,
        )


@app.get("/")
async def get_root() -> AllTransitInfo:
    return await fetch_all_info()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
