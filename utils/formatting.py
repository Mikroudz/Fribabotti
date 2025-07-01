from datetime import datetime
from zoneinfo import ZoneInfo
import random
import string


def datetime_to_pretty(
    date: datetime, timezone: str = "UTC", pretty_print=True
) -> str | datetime:
    if not date:
        return ""
    target_timez = ZoneInfo(timezone)
    converted = date.astimezone(target_timez)
    return converted.strftime("%Y-%m-%d %H:%M:%S") if pretty_print else converted


def par_score_format(val: int) -> str:
    return f"{val:+g}" if val != 0 else str(val)


def create_uuid(len: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=len))
