from typing import List, Tuple
from sqlmodel import Session, select, and_, asc, desc, func, case, cast, Integer
from sqlalchemy.orm import selectinload, with_loader_criteria
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta

from .model import (
    GameSession,
    GameSessionReadLong,
    GameSessionReadShort,
    GameSessionUserStats,
    GameSessionReadDevice,
    HoleReadDevice,
    ThrowShortDevice,
)
from models.user.model import User
from models.user.crud import read_user
from models.track.model import Track, HoleReadLong

from models.course.model import Course
from models.score.model import Score, CourseScore

from models.user_group.model import UserGroup
from models.links.session_participants_link import SessionParticipantsLink
from models.links.user_group_members_link import UserGroupMembersLink
import logging

logger = logging.getLogger(__name__)


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
    session: Session,
    user_id: int,
    active: bool | None = True,
    course_id: int | None = None,
    limit: int | None = None,
) -> List[GameSessionReadShort]:
    """Read game sessions where user is participating

    Args:
      session: Active DB session
      user_id: ID which user's sessions to search
      active(True|False|None): Returns active or ended game sessions. If passed None, returns active and ended sessions.

    Returns:
        List of GameSessions with Courses loaded (eg. GameSession.course)

    """

    subq = (
        select(
            Score.game_session_id,
            func.sum(Score.score).label("score"),
            func.sum(Track.par).label("par"),
        )
        .join(
            Track,
            and_(
                Track.course_id == Score.course_id,
                Track.track_number == Score.track_number,
            ),
        )
        .where(and_(Score.user_id == user_id))
        .group_by(Score.game_session_id)
        .subquery()
    )
    stmt = (
        select(
            GameSession,
            func.coalesce(subq.c.score, 0).label("score"),
            func.coalesce(subq.c.par, 0).label("par"),
        )
        .options(selectinload(GameSession.course))
        .join(
            SessionParticipantsLink,
            GameSession.id == SessionParticipantsLink.game_session_id,
        )
        .outerjoin(
            subq,
            GameSession.id == subq.c.game_session_id,
        )
        .where(SessionParticipantsLink.user_id == user_id)
        .order_by(GameSession.ended_at.is_(None).desc(), GameSession.ended_at.desc())
    )

    if active is not None:
        if active:
            stmt = stmt.where(GameSession.ended_at.is_(None))
        else:
            stmt = stmt.where(GameSession.ended_at.is_not(None))
    if course_id is not None:
        stmt = stmt.where(GameSession.course_id == course_id)
    stmt = stmt.order_by(desc(GameSession.started_at))
    if limit is not None:
        stmt = stmt.limit(limit)
    ret = session.exec(stmt).all()
    return [
        GameSessionReadShort(
            **game.model_dump(), user_score=score, par=par, course=game.course
        )
        for game, score, par in ret
    ]


def read_game_session_long(
    session: Session, user_id: int, game_session_id: int
) -> GameSessionReadLong | None:

    db_type = session.bind.dialect.name
    if db_type == "sqlite":
        end_sec = func.unixepoch(func.max(Score.created_at))
        start_sec = func.unixepoch(func.min(Score.created_at))
        time_diff = end_sec - start_sec
    else:
        time_diff = func.unix_timestamp(
            func.max(Score.created_at)
        ) - func.unix_timestamp(func.min(Score.created_at))

    # note that playtime is limited to 6 hours; set to 0 if we go over that (something weird has happened with the scores)
    stmt = (
        select(
            GameSession,
            case(
                (time_diff > (6 * 3600), 0), (time_diff == None, 0), else_=time_diff
            ).label("playtime"),
        )
        .options(
            selectinload(GameSession.course).selectinload(Course.tracks),
            selectinload(GameSession.scores).selectinload(Score.throws),
            selectinload(GameSession.user_group),
        )
        .join(
            SessionParticipantsLink,
            GameSession.id == SessionParticipantsLink.game_session_id,
        )
        .outerjoin(Score, Score.game_session_id == GameSession.id)
        .where(
            and_(
                SessionParticipantsLink.user_id == user_id,
                GameSession.id == game_session_id,
            )
        )
    )
    res = session.exec(stmt).first()
    if res == None:
        return None
    res, playtime = res
    # TODO: actually get scores for all users if requested idk
    user = read_user(session, user_id)

    scores = CourseScore(user_id=user_id, **user.model_dump())
    track_total_par = 0
    score_total = 0

    for track in res.course.tracks:
        track_num = track.track_number
        find_score = [score for score in res.scores if score.track_number == track_num]
        throws = []
        score = 0
        track_total_par += track.par
        if len(find_score) > 0:
            score = find_score[0].score
            score_total += score
            for throw in find_score[0].throws:
                throws.append(throw)
        scores.scores.append(
            HoleReadLong(**track.model_dump(), throws=throws, score=score)
        )
    scores.par = track_total_par
    scores.total_score = score_total
    game = GameSessionReadLong(
        id=game_session_id,
        course_id=res.course_id,
        course=res.course,
        user_group_id=res.user_group_id,
        user_group=res.user_group,
        user_score=scores,
        started_at=res.started_at,
        ended_at=res.ended_at,
        playtime=playtime,
    )
    return game


# specific formatting for devices
def read_game_session_device(
    session: Session, session_id: int, user_id: int
) -> GameSessionReadDevice:
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
        .options(selectinload(Score.throws))
        .join(GameSession, GameSession.id == session_id)
        .where(and_(Track.deleted == False, Track.course_id == GameSession.course_id))
        .order_by(Track.track_number)
    )

    data = session.exec(stmt).all()
    holes = []

    for score, track in data:
        throws = []
        if score:
            cnt_throws_with_loc = 0
            for index, throw in enumerate(score.throws):
                if throw.start_lat and throw.start_lat:
                    cnt_throws_with_loc += 1
                    throws.append(
                        ThrowShortDevice(lat=throw.start_lat, lng=throw.start_lat)
                    )
            if score.score > len(throws):
                throws += [None] * (score.score - len(throws) + 1)

        holes.append(HoleReadDevice(throws=throws, par=track.par))

    return GameSessionReadDevice(holes=holes)


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
        .join(UserGroup, GameSession.user_group_id == UserGroup.id)
        .join(UserGroupMembersLink, UserGroup.id == UserGroupMembersLink.user_group_id)
        .outerjoin(
            SessionParticipantsLink,
            and_(
                GameSession.id == SessionParticipantsLink.game_session_id,
                SessionParticipantsLink.user_id == user_id,
            ),
        )
        .where(
            and_(
                UserGroupMembersLink.user_id == user_id,
                GameSession.ended_at.is_(None),
                SessionParticipantsLink.user_id.is_(None),
            )
        )
        .order_by(desc(GameSession.started_at))
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


def read_game_session(session: Session, session_id: int) -> GameSession | None:
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
            selectinload(GameSession.participants),
            selectinload(GameSession.course),
            selectinload(GameSession.user_group),
            selectinload(GameSession.scores),
        )
        .where(GameSession.id == session_id)
    )
    return session.exec(stmt).first()


def end_game_session(
    session: Session, session_id: int, close: bool = True, read: bool = True
):
    db_session = session.get(GameSession, session_id)
    if db_session:
        setattr(db_session, "ended_at", datetime.now(timezone.utc) if close else None)
        session.add(db_session)
        session.commit()
        return read_game_session(session, session_id) if read else {"status": "ok"}


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


def join_game_session(session: Session, user_id: int, session_id: int) -> None:
    db_check_if_user_in_session = session.exec(
        select(SessionParticipantsLink).where(
            and_(
                SessionParticipantsLink.user_id == int(user_id),
                SessionParticipantsLink.game_session_id == int(session_id),
            )
        )
    ).first()

    if db_check_if_user_in_session != None:
        return
    db_user = session.get(User, user_id)
    db_session = session.get(GameSession, int(session_id))

    if db_user and db_session:
        participant = SessionParticipantsLink(
            game_session_id=int(session_id), user_id=user_id
        )
        session.add(participant)
        session.commit()


def read_user_session_time(
    session: Session, user_id: int, from_time: datetime
) -> tuple[int, int]:

    db_type = session.bind.dialect.name
    if db_type == "sqlite":
        end_sec = func.unixepoch(GameSession.ended_at)
        start_sec = func.unixepoch(GameSession.started_at)
        time_diff = end_sec - start_sec

    elif db_type in ["mysql", "mariadb"]:
        time_diff = func.unix_timestamp(GameSession.ended_at) - func.unix_timestamp(
            GameSession.started_at
        )

    stmt = (
        select(
            func.count(GameSession.id),
            func.sum(time_diff),
        )
        .join(
            SessionParticipantsLink,
            GameSession.id == SessionParticipantsLink.game_session_id,
        )
        .where(SessionParticipantsLink.user_id == user_id)
        .where(GameSession.started_at > from_time)
    )

    count, total_timedelta = session.exec(stmt).first()
    if isinstance(total_timedelta, datetime):
        total_timedelta = total_timedelta.total_seconds()
    return count, total_timedelta


def read_user_stats(
    session: Session, user_id: int, days_to_past: int
) -> GameSessionUserStats:
    start_n_days_ago = datetime.now() - timedelta(days=days_to_past)

    db_type = session.bind.dialect.name
    if db_type == "sqlite":
        time_diff = (
            func.julianday(func.max(Score.created_at))
            - func.julianday(func.min(Score.created_at))
        ) * 86400
    else:
        time_diff = func.unix_timestamp(
            func.max(Score.created_at)
        ) - func.unix_timestamp(func.min(Score.created_at))

    round_totals = (
        select(
            Score.game_session_id,
            case(
                (time_diff > (6 * 3600), 0),
                (time_diff.is_(None), 0),
                else_=cast(time_diff, Integer),
            ).label("playtime"),
        )
        .where(
            Score.user_id == user_id,
            Score.score > 0,
            Score.created_at > start_n_days_ago,
            Score.created_at.isnot(None),
        )
        .group_by(Score.game_session_id)
        .subquery()
    )

    stmt_avg_play_cnt = select(
        func.count(round_totals.c.game_session_id).label("game_count"),
        func.coalesce(func.sum(round_totals.c.playtime), 0).label("playtime"),
    ).select_from(round_totals)
    db_stats = session.exec(stmt_avg_play_cnt).first()

    return GameSessionUserStats(
        playtime=db_stats.playtime, playcount=db_stats.game_count
    )
