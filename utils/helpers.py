from datetime import datetime, UTC, timezone
import math


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calc_short_distance(p1: tuple[float, float], p2: tuple[float, float]):

    x = (((p2[1] - p1[1]) * math.pi) / 180) * math.cos(
        ((p1[0] + p2[0]) * math.pi) / 360
    )
    y = ((p2[0] - p1[0]) * math.pi) / 180

    return math.sqrt(x * x + y * y) * 6371000
