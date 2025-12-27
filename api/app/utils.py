import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, defaultValue: Optional[str] = None) -> str:
    v = os.getenv(key) or defaultValue

    if v is None:
        raise EnvironmentError("Missing required env var: " + key)

    return v


def now() -> int:
    return int(datetime.now().timestamp())


def unwrap[T](v: T | None) -> T:
    assert v is not None
    return v
