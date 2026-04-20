from datetime import datetime, timedelta, timezone


BEIJING_OFFSET = timedelta(hours=8)


def to_beijing(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None) + BEIJING_OFFSET
    return value + BEIJING_OFFSET


def beijing_iso(value: datetime | None) -> str | None:
    local_value = to_beijing(value)
    return local_value.isoformat() if local_value else None


def beijing_strftime(value: datetime | None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    local_value = to_beijing(value)
    return local_value.strftime(fmt) if local_value else ""
