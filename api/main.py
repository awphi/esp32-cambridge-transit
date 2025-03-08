import threading
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from bus_info import BusInfo, fetch_bus_info
from utils import now


class TransitInfo(BaseModel):
    time: int
    bus_info: List[BusInfo]


transit_info = TransitInfo(time=now(), bus_info=list())
transit_info_timer: Optional[threading.Timer] = None


def update_transit_info() -> None:
    global transit_info, transit_info_timer
    bus_info = fetch_bus_info()
    transit_info = TransitInfo(time=now(), bus_info=bus_info)
    transit_info_timer = threading.Timer(60.0, update_transit_info).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global transit_info_timer
    update_transit_info()
    yield
    if transit_info_timer is not None:
        transit_info_timer.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def get_root() -> TransitInfo:
    return transit_info
