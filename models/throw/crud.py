from typing import List, Tuple
from sqlmodel import Session, select, not_, and_, exists, func, desc, asc
from sqlalchemy.orm import selectinload, with_loader_criteria
from .model import Throw, ThrowCreate, ThrowUpdate
from models.score.model import Score
from models.score.crud import upsert_score, read_score
from fastapi import HTTPException


import logging

logger = logging.getLogger(__name__)


def create_throw(session: Session, throw: ThrowCreate, user_id: int) -> Score | None:

    db_score = session.exec(
        select(Score)
        .options(selectinload(Score.throws))
        .where(
            and_(
                Score.track_number == throw.track_number,
                Score.game_session_id == throw.game_session_id,
                Score.user_id == user_id,
            )
        )
    ).first()

    # score is created with 0 as we dont count first throw as a full throw
    score = 0
    if db_score:
        # add one throw TODO: roll back this value if score creation fails
        score = db_score.score + 1

    # update or create score
    db_score = upsert_score(
        session, score, throw.track_number, user_id, throw.game_session_id
    )
    # in this case score is not created or update fails, cannot continue
    if not db_score:
        raise HTTPException(404, "Score creation failed")

    new_throw = Throw(score_id=db_score.id, **throw.model_dump())
    if len(db_score.throws) > 0:
        # need to update previous throw end position
        prev_throw = sorted(
            db_score.throws, key=lambda t: t.throw_number, reverse=False
        )[-1]
        if throw.start_lat:
            prev_throw.end_lat = throw.start_lat
        if throw.start_lng:
            prev_throw.end_lng = throw.start_lng
        session.add(prev_throw)
        new_throw.throw_number = prev_throw.throw_number + 1
    else:
        new_throw.throw_number = 1
    session.add(new_throw)
    session.commit()
    return read_score(session, db_score.id)


def update_throw(session: Session, throw: ThrowUpdate, user_id: int) -> int:
    stmt = select(Throw).where(Throw.id == throw.id)
    db_throw = session.exec(stmt).first()

    if not db_throw:
        raise HTTPException(404, "Throw does not exist")
    db_throw.sqlmodel_update(throw)

    # we need to update next and previous throws also if they exist
    stmt = (
        select(Throw)
        .where(
            and_(
                Throw.score_id == db_throw.score_id,
                Score.user_id == user_id,
            )
        )
        .join(Throw.score)
        .order_by(Throw.throw_number.asc())
    )
    all_throws = session.exec(stmt).all()

    curr_throw_id = next(
        (i for i, d in enumerate(all_throws) if d.id == db_throw.id), None
    )
    prev_throw = all_throws[curr_throw_id - 1] if curr_throw_id - 1 >= 0 else None
    next_throw = (
        all_throws[curr_throw_id + 1] if curr_throw_id + 1 < len(all_throws) else None
    )
    if prev_throw:
        if throw.start_lat:
            prev_throw.end_lat = throw.start_lat
        if throw.start_lng:
            prev_throw.end_lng = throw.start_lng
        session.add(prev_throw)
    # Do we even need this?
    if next_throw:
        if throw.end_lat:
            next_throw.start_lat = throw.end_lat
        if throw.end_lng:
            next_throw.start_lng = throw.end_lng
        session.add(next_throw)

    session.commit()

    return db_throw.score_id


def remove_throw(session: Session, throw_id: int, user_id: int) -> Score:
    # HUGE NOTE: this expects we always delete last throw and not in between throws
    # If we need to delete between throws then should update previous and next throw end/start positions
    # I think throws should be recorded somehow differently (not have both start/end pos at each throw)
    throw = session.get(Throw, throw_id)
    if throw:
        # Remove end position of previous throw
        stmt = (
            select(Throw)
            .where(
                and_(
                    Throw.score_id == throw.score_id,
                    Score.user_id == user_id,
                )
            )
            .join(Throw.score)
            .order_by(Throw.throw_number.asc())
        )
        throws = session.exec(stmt).all()
        curr_throw_id = next(
            (i for i, d in enumerate(throws) if d.id == throw.id), None
        )
        prev_throw = throws[curr_throw_id - 1] if curr_throw_id - 1 >= 0 else None
        if prev_throw:
            if throw.start_lat:
                prev_throw.end_lat = None
            if throw.start_lng:
                prev_throw.end_lng = None
            session.add(prev_throw)

        # set this throw deleted
        score_id = throw.score_id
        session.delete(throw)
        # update score
        db_score = session.get(Score, throw.score_id)
        new_score = max(db_score.score - 1, 0)
        upsert_score(
            session,
            new_score,
            db_score.track_number,
            db_score.user_id,
            db_score.game_session_id,
        )
        session.commit()
        return read_score(session, score_id)
