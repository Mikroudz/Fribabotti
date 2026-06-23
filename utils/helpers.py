from datetime import datetime, UTC, timezone
import math
from sqlmodel import Session, select
from sqlalchemy.orm import aliased


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calc_short_distance(p1: tuple[float, float], p2: tuple[float, float]):

    x = (((p2[1] - p1[1]) * math.pi) / 180) * math.cos(
        ((p1[0] + p2[0]) * math.pi) / 360
    )
    y = ((p2[0] - p1[0]) * math.pi) / 180

    return math.sqrt(x * x + y * y) * 6371000


def get_first_available_id(session, model_class) -> int:
    id_one_exists = session.scalar(
        select(model_class.id).filter(model_class.id == 1).limit(1)
    )
    if not id_one_exists:
        return 1

    t1 = model_class
    t2 = aliased(model_class)

    stmt = (
        select((t1.id + 1).label("next_id"))
        .outerjoin(t2, t2.id == t1.id + 1)
        .where(t2.id == None)  # Gap found
        .order_by("next_id")
        .limit(1)
    )

    return session.scalar(stmt)
