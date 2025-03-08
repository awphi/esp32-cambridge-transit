import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, defaultValue: Optional[str]) -> str:
    v = os.getenv(key) or defaultValue

    if v is None:
        raise EnvironmentError("Missing required env var: " + key)

    return v
