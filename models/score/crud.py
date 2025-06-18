from typing import List, Tuple
from sqlmodel import Session, select, not_, and_, exists, func, desc, asc
from pydantic import ValidationError
from sqlalchemy.orm import selectinload, with_loader_criteria
from .model import Score
from models.course.model import Course
from models.track.model import Track
from models.user.model import User
from models.game_session.model import GameSession
import logging

logger = logging.getLogger(__name__)


def upsert_score(
    session: Session, score: int, track_number: int, user_id: int, game_session_id: int
) -> Score | None:
    # Update if exists
    db_score = session.exec(
        select(Score).where(
            and_(
                Score.track_number == track_number,
                Score.game_session_id == game_session_id,
            )
        )
    ).first()
    if db_score:
        db_score.sqlmodel_update(Score(score=score).model_dump(exclude_unset=True))
        session.commit()
        session.refresh(db_score)
        return db_score
    session_stmt = select(GameSession).where(game_session_id == GameSession.id)
    db_session: GameSession = session.exec(session_stmt).first()

    if not db_session:
        return None

    # creating score, check everything exists
    track_stmt = select(Track).where(
        and_(
            track_number == Track.track_number, Track.course_id == db_session.course_id
        )
    )
    user_stmt = select(User).where(user_id == User.id)

    stmt = select(
        and_(
            exists(track_stmt),
            exists(user_stmt),
        )
    )
    dependent_exists = session.exec(stmt).first()

    if dependent_exists:

        try:
            score = Score(
                score=score,
                track_number=track_number,
                course_id=db_session.course_id,
                user_id=user_id,
                game_session_id=game_session_id,
            )
        except ValidationError as e:
            logger.warning(e)
            return None
        session.add(score)
        session.commit()
        session.refresh(score)
        return score


def delete_score(session: Session, score_id: int):
    db_score = session.get(Score, score_id)
    if db_score:
        session.delete(db_score)


def update_score(session: Session, score_id: int, score: int) -> Score:
    db_score = session.get(Score, score_id)

    if db_score:
        db_score.sqlmodel_update(Score(score=score).model_dump(exclude_unset=True))
        session.commit()
        session.refresh(db_score)
        return db_score


def read_users_scores(session: Session, session_id: int) -> List[Tuple[int, User]]:
    stmt = (
        select(func.sum(Score.score).label("score_sum"), User)
        .join(User, Score.user_id == User.id)
        .where(Score.game_session_id == session_id)
        .group_by(User.id)
        .order_by(desc("score_sum"))
    )

    scores = session.exec(stmt).all()
    return scores


def read_session_username_score_full(
    session: Session, session_id: int, course_id: int
) -> List[Tuple[str, Score]]:
    stmt = (
        select(User.username, Score)
        .options(
            selectinload(Score.track),
            with_loader_criteria(Track, Track.deleted == False),
        )
        .join(User, Score.user_id == User.id)
        .join(
            Track,
            # Score.track_number == Track.track_number,
            # Track.course_id == course_id,
        )
        .where(Score.game_session_id == session_id)
        .order_by(asc(Track.track_number))
    )

    scores = session.exec(stmt).all()
    return scores


def read_scores(
    session: Session, session_id: int, user_id: int
) -> List[Tuple[Score, Track]]:
    stmt = (
        select(Score, Track)
        .join(
            Score,
            and_(
                Track.track_number == Score.track_number,
                Score.user_id == user_id,
                Score.game_session_id == session_id,
            ),
            isouter=True,
        )
        .join(GameSession, GameSession.id == session_id)
        .where(and_(Track.deleted == False, Track.course_id == GameSession.course_id))
        # .where(and_(Score.game_session_id == session_id, Score.user_id == user_id))
        .order_by(Track.track_number)
    )
    return session.exec(stmt).all()
