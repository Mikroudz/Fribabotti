from typing import List, Tuple
from sqlmodel import Session, select, not_, and_, exists, func, desc, asc
from pydantic import ValidationError
from sqlalchemy.orm import selectinload, with_loader_criteria
from .model import Score
from models.track.model import Track
from models.user.model import User
from models.links.session_participants_link import SessionParticipantsLink
from models.game_session.model import UpdateGameSession
from datetime import datetime

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
                Score.user_id == user_id,
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


def update_game_session(
    session: Session, game_session_id: int, user_id: int, throws: UpdateGameSession
) -> dict:

    stmt = select(Score).where(
        Score.game_session_id == game_session_id, Score.user_id == user_id
    )
    existing_scores = session.exec(stmt).all()
    score_dict = {score.track_number: score for score in existing_scores}

    course_id = None
    if existing_scores:
        course_id = existing_scores[0].course_id
    else:
        stmt = select(GameSession.course_id).where(GameSession.id == game_session_id)
        course_id = session.exec(stmt).first()

    stmt = select(Track).where(course_id == Track.course_id)
    tracks = session.exec(stmt).all()

    par_dict = {track.track_number: track.par for track in tracks}
    print(throws)
    print(existing_scores)
    for index, throw_list in enumerate(throws.throws):
        track_number = index + 1
        calculated_score = len(throw_list) - par_dict[track_number]

        # Optional: If the list is empty, you might want to save None instead of 0
        # so it doesn't mess up averages. Uncomment the line below if so:
        # calculated_score = calculated_score if calculated_score > 0 else None

        # 5. Check if the score exists in the database
        if track_number in score_dict:
            # Update existing score if it has changed
            db_score = score_dict[track_number]
            if db_score.score != calculated_score:
                db_score.score = calculated_score
                session.add(db_score)
        else:
            # Insert a newly played track
            # (Only happens if scores aren't pre-generated when the game starts)
            if calculated_score > 0:  # Optionally only create if they actually threw
                new_score = Score(
                    score=calculated_score,
                    track_number=track_number,
                    course_id=course_id,  # Requires course_id to satisfy your ForeignKey
                    user_id=user_id,
                    game_session_id=game_session_id,
                )
                session.add(new_score)
    session.commit()
    return {"status": "ok"}


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
    session_scores_sq = (
        select(Score.user_id, Score.score)
        .join(GameSession, Score.game_session_id == GameSession.id)
        .where(GameSession.id == session_id)
        .subquery()
    )

    stmt = (
        select(
            User,
            func.coalesce(func.sum(session_scores_sq.c.score), 0).label("score_sum"),
        )
        .join(User, SessionParticipantsLink.user_id == User.id)
        .select_from(SessionParticipantsLink)
        .outerjoin(session_scores_sq, User.id == session_scores_sq.c.user_id)
        .where(SessionParticipantsLink.game_session_id == session_id)
        .group_by(User.id)
        .order_by(desc("score_sum"))
    )

    scores = session.exec(stmt).all()
    return scores


def read_course_user_top_scores(
    session: Session, user_id: int, course_id: int
) -> List[Tuple[int, int]]:

    stmt = (
        select(
            Score.game_session_id,
            func.coalesce(func.sum(Score.score), 0).label("score_sum"),
        )
        .join(GameSession, Score.game_session_id == GameSession.id)
        .where(and_(Score.user_id == user_id, GameSession.course_id == course_id))
        .group_by(Score.game_session_id)
        .order_by(asc("score_sum"))
    )

    scores = session.exec(stmt).all()
    return scores


def read_session_username_score_full(
    session: Session, session_id: int
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


def read_course_best_user_scores(
    session: Session,
    user_id: int,
    course_id: int | None = None,
    session_id: int | None = None,
) -> List[Tuple[int, int, datetime]] | List:

    if session_id is not None:
        game_session = session.get(GameSession, session_id)
        if not game_session:
            return []
        course_id = game_session.course_id

    if course_id is None:
        return []

    s_stmt = (
        select(
            Score.track_number,
            Score.score,
            GameSession.started_at,
            func.row_number()
            .over(
                partition_by=Score.track_number,
                order_by=[Score.score.asc(), GameSession.started_at.desc()],
            )
            .label("rn"),
        )
        .join(GameSession, Score.game_session_id == GameSession.id)
        .where(and_(Score.user_id == user_id, Score.course_id == course_id))
        .subquery()
    )

    stmt = (
        select(
            s_stmt.c.track_number,
            s_stmt.c.score,
            s_stmt.c.started_at,
        )
        .where(s_stmt.c.rn == 1)
        .order_by(s_stmt.c.track_number)
    )

    return session.exec(stmt).all()
