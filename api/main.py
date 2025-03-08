import asyncio
from contextlib import asynccontextmanager
from typing import Any, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from bus_info import BusInfo, fetch_bus_info
from utils import now


class TransitInfo(BaseModel):
    time: int = Field(default_factory=lambda: now())
    bus_info: List[BusInfo] = Field(default=[])
    train_info: List[Any] = Field(default=[])


transit_info = TransitInfo()


async def update_transit_info() -> None:
    global transit_info

    while True:
        transit_info = TransitInfo(bus_info=fetch_bus_info())
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(update_transit_info())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get_root() -> TransitInfo:
    return transit_info
