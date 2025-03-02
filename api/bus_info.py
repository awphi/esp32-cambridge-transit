import os
from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class BusInfo(BaseModel):
    eta: str
    service: str
    dest: str


def fetch_bus_info() -> List[BusInfo]:
    url: str = (
        "https://www.cambridgeshirebus.info/Popup_Content/WebDisplay/WebDisplay.aspx?stopRef="
        + os.getenv("BUS_STOP_REF")
    )
    r = requests.get(url)
    result: List[BusInfo] = []

    if r.ok:
        soup = BeautifulSoup(r.text, features="html.parser")
        table = soup.select_one(".rtiTable")
        for row in table.select(".gridRow"):
            service = row.select_one(".gridServiceItem").get_text()
            dest = row.select_one(".gridDestinationItem").get_text()
            eta = row.select_one(".gridTimeItem").get_text()
            result.append(BusInfo(eta=eta, service=service, dest=dest))

    return result
