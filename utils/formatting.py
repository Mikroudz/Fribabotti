from datetime import datetime
from zoneinfo import ZoneInfo


def datetime_to_pretty(date: datetime, timezone: str = "UTC") -> str:
    target_timez = ZoneInfo(timezone)
    converted = date.astimezone(target_timez)
    return converted.strftime("%Y-%m-%d %H:%M:%S")


def par_score_format(val: int) -> str:
    return f"{val:+g}" if val != 0 else str(val)
