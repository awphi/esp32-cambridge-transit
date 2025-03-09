from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from utils import get_env


class BusInfo(BaseModel):
    eta: str
    service: str
    dest: str


def unwrap[T](v: T | None) -> T:
    assert v is not None
    return v


def fetch_bus_info() -> List[BusInfo]:
    url: str = (
        "https://www.cambridgeshirebus.info/Popup_Content/WebDisplay/WebDisplay.aspx?stopRef="
        + get_env("BUS_STOP_REF")
    )

    r = requests.get(url)
    result: List[BusInfo] = []

    if r.ok:
        soup = BeautifulSoup(r.text, features="html.parser")
        # unsafe unwrapping of Optional values but fine for now
        table = unwrap(soup.select_one(".rtiTable"))
        for row in table.select(".gridRow"):
            service = unwrap(row.select_one(".gridServiceItem")).get_text()
            dest = unwrap(row.select_one(".gridDestinationItem")).get_text()
            eta = unwrap(row.select_one(".gridTimeItem")).get_text()
            result.append(BusInfo(eta=eta, service=service, dest=dest))

    return result
