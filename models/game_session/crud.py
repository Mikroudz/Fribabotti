from typing import List, Tuple
from sqlmodel import Session, select, and_
from sqlalchemy.orm import selectinload, with_loader_criteria
from pydantic import ValidationError
from datetime import datetime, timezone

from .model import GameSession
from models.user.model import User
from models.track.model import Track

from models.course.model import Course
from models.user_group.model import UserGroup
from models.links.session_participants_link import SessionParticipantsLink
from models.links.user_group_members_link import UserGroupMembersLink


def create_game_session(
    session: Session, user_id: int, course_id: int, user_group_id: int | None
) -> GameSession | None:

    db_user = session.get(User, user_id)
    db_course = session.get(Course, course_id)
    if user_group_id:
        db_user_group = session.get(UserGroup, user_group_id)
    if db_course and db_user:
        try:
            game = GameSession(
                participants=[db_user], user_group=db_user_group, course=db_course
            )
        except ValidationError as e:
            raise e
        session.add(game)
        session.commit()
        session.refresh(game)
        return session.exec(
            select(GameSession)
            .options(selectinload(GameSession.course))
            .where(GameSession.id == game.id)
        ).first()


def read_game_session_user(
    session: Session, user_id: int, active: bool = True
) -> List[GameSession]:
    """Read game sessions where user is participating

    Args:
      session: Active DB session
      user_id: ID which user's sessions to search
      active: Returns active or ended game sessions

    Returns:
        List of GameSessions with Courses loaded (eg. GameSession.course)

    """

    stmt = (
        select(GameSession)
        .options(selectinload(GameSession.course))
        .join(
            SessionParticipantsLink,
            GameSession.user_group_id == SessionParticipantsLink.game_session_id,
        )
        .where(
            and_(
                SessionParticipantsLink.user_id == user_id,
                (
                    GameSession.ended_at == None
                    if active
                    else GameSession.ended_at != None
                ),
            )
        )
    )
    return session.exec(stmt).all()


def read_game_session_user_groups(session: Session, user_id: int) -> List[GameSession]:
    """Read game sessions from groups user is in

    Args:
      session: Active DB session
      user_id: ID which user's sessions to search

    Returns:
        List of GameSessions with courses loaded

    """

    stmt = (
        select(GameSession)
        .options(selectinload(GameSession.course))
        .join(
            UserGroup,
            UserGroup.id == GameSession.user_group_id,
        )
        .join(
            UserGroupMembersLink,
            UserGroup.id == UserGroupMembersLink.user_id,
        )
        .where(
            and_(UserGroupMembersLink.user_id == user_id, GameSession.ended_at == None)
        )
    )
    return session.exec(stmt).all()


def read_game_session_course(session: Session, session_id: int) -> Course:
    stmt = (
        select(Course)
        .options(
            selectinload(Course.tracks),
            with_loader_criteria(Track, Track.deleted == False),
        )
        .join(GameSession, Course.id == GameSession.course_id)
        .where(GameSession.id == session_id)
    )
    return session.exec(stmt).first()


def read_game_session(session: Session, session_id: int) -> GameSession:
    """Read game session

    Args:
      session: Active DB session
      session_id: GameSession id

    Returns:
        GameSession

    """
    stmt = (
        select(GameSession)
        .options(
            selectinload(
                GameSession.participants,
            ),
            selectinload(GameSession.course),
            selectinload(GameSession.user_group),
            selectinload(GameSession.scores),
        )
        .where(GameSession.id == session_id)
    )
    return session.exec(stmt).first()


def end_game_session(session: Session, session_id: int):

    db_session = session.get(GameSession, session_id)
    if db_session:
        setattr(db_session, "ended_at", datetime.now(timezone.utc))
        session.commit()
        return read_game_session(session, session_id)


def reopen_game_session(session: Session, session_id: int):
    db_session = session.get(GameSession, session_id)
    if db_session:
        setattr(db_session, "ended_at", None)
        session.commit()
        session.refresh(db_session)
        return db_session


def delete_game_session(session: Session, game_session_id: int):
    db_game_session = session.get(GameSession, game_session_id)
    if db_game_session:
        session.delete(db_game_session)
        session.commit()


def join_game_session(session: Session, user_id: int, session_id: int):
    db_user = session.get(User, user_id)
    db_session = session.get(Course, session_id)

    if db_user and db_session:
        participant = SessionParticipantsLink(
            game_session_id=session_id, user_id=user_id
        )
        session.add(participant)
        session.commit()
