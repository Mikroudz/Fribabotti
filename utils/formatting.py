from datetime import datetime
from zoneinfo import ZoneInfo
import random
import string


def convert_to_timezone(value: datetime, tz: str) -> datetime:
    target_timez = ZoneInfo(tz)
    return value.astimezone(target_timez)


def datetime_to_pretty(
    date: datetime, timezone: str = "UTC", pretty_print=True
) -> str | datetime:
    if not date:
        return ""
    converted = convert_to_timezone(date, timezone)
    return converted.strftime("%Y-%m-%d %H:%M:%S") if pretty_print else converted


def par_score_format(val: int) -> str:
    return f"{val:+g}" if val != 0 else str(val)


def create_uuid(len: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=len))
