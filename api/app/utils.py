from datetime import datetime


def now() -> int:
    return int(datetime.now().timestamp())


def unwrap[T](v: T | None) -> T:
    assert v is not None
    return v
