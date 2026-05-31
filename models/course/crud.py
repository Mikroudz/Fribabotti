from typing import List
from sqlmodel import Session, select, and_, func, delete, col, case, cast, Integer
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from pydantic import ValidationError

from .model import Course, CourseUpdate, CourseCreate, CourseReadShort
from .stat_model import CourseWithStats, CourseStatHistory

from models.track.model import Track
from models.game.model import Game
from models.score.model import Score
from models.game_session.crud import read_game_session_user
from models.game_session.model import (
    GameSessionReadShortWithoutCourse,
    GameSession,
    GameSessionReadStat,
)


def create_course(
    session: Session, name: str, location: str | None, game_id: int
) -> Course:
    db_game = session.get(Game, game_id)
    if db_game:
        try:
            course = Course(name=name, location=location, game=db_game)
        except ValidationError as e:
            raise e
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


def create_course_with_tracks(
    session: Session, course: CourseCreate, game_id: int
) -> Course:
    db_game = session.get(Game, game_id)
    if db_game:
        course_dict = course.model_dump()
        tracks = course_dict.pop("tracks")

        course = Course(**course_dict, game_id=game_id)

        session.add(course)
        session.commit()
        session.refresh(course)
        if len(tracks) > 0:
            session.add_all([Track(**track, course_id=course.id) for track in tracks])
        session.commit()
        return course


def update_course_with_tracks(
    session: Session, course_id: int, update_data: CourseUpdate
) -> Course | None:
    db_course = session.get(Course, course_id)
    if db_course:
        course_dict = update_data.model_dump(exclude_unset=True)
        tracks = course_dict.pop("tracks")
        db_course.sqlmodel_update(course_dict)
        session.commit()
        session.refresh(db_course)
        stmt = select(Track).where(Track.course_id == course_id)
        db_tracks = session.exec(stmt).all()
        db_tracks = {track.track_number: track for track in db_tracks}

        to_delete = [
            track
            for track_number, track in db_tracks.items()
            if not any(
                incoming_track.get("track_number") == track_number
                for incoming_track in tracks
            )
        ]

        session.exec(
            delete(Track).where(
                and_(
                    Track.course_id == course_id,
                    col(Track.track_number).in_(
                        [track.track_number for track in to_delete]
                    ),
                )
            )
        )

        for track in tracks:
            db_track = db_tracks.get(track["track_number"], None)
            if db_track:
                if track.get("par") != None and db_track.par != track["par"]:
                    setattr(db_track, "par", track["par"])
                    session.add(db_track)
            else:
                # new
                new_track = Track(**track, course_id=course_id)
                session.add(new_track)
        session.commit()
        return db_course


def update_course(
    session: Session, course_id: int, update_data: CourseUpdate
) -> Course | None:
    db_course = session.get(Course, course_id)
    if db_course:
        db_course.sqlmodel_update(update_data.model_dump(exclude_unset=True))
        session.commit()
        session.refresh(db_course)
        return db_course


def delete_course(session: Session, course_id: int):
    db_course = session.exec(
        select(Course)
        .options(selectinload(Course.game_sessions))
        .where(Course.id == course_id)
    ).first()
    if db_course:
        if len(db_course.game_sessions) == 0:
            session.delete(db_course)
        else:
            setattr(db_course, "deleted", True)
            session.add(db_course)
        session.commit()


def read_courses(
    session: Session, game_id: int | None = None
) -> List[tuple[Course, int]]:
    stmt = select(Course, func.sum(Track.par).label("par")).join(Track)
    if game_id:
        stmt = stmt.where(Course.game_id == game_id)

    courses = session.exec(stmt).all()
    return courses


def read_courses_short(
    session: Session, game_id: int | None = None
) -> List[CourseReadShort]:
    stmt = (
        select(Course, func.count(Track.track_number).label("holes"))
        .join(Track, Track.course_id == Course.id)
        .group_by(Course.id)
    )
    if game_id:
        stmt = stmt.where(Course.game_id == game_id)

    courses = session.exec(stmt).all()
    return [
        CourseReadShort(**course.model_dump(), holes=holes) for course, holes in courses
    ]


def read_course(session: Session, course_id: int) -> Course:
    db_course = session.get(Course, course_id)

    return db_course


def read_courses_short_stats(
    session: Session, user_id: int, game_id: int | None = None
) -> List[CourseReadShort]:

    course_stats = (
        select(
            Score.course_id,
            func.sum(Score.score).label("round_total"),
            func.sum(Track.par).label("par"),
        )
        .join(
            Track,
            and_(
                Track.course_id == Score.course_id,
                Track.track_number == Score.track_number,
            ),
        )
        .where(Score.user_id == user_id)
        .group_by(Score.course_id)
        .subquery()
    )

    stmt = select(
        Course,
        func.coalesce(course_stats.c.round_total, 0).label("user_total_score"),
        func.coalesce(course_stats.c.par, 0).label("user_total_par"),
    ).outerjoin(course_stats, Course.id == course_stats.c.course_id)
    if game_id:
        stmt = stmt.where(Course.game_id == game_id)

    courses = session.exec(stmt).all()
    return [
        CourseReadShort(**course.model_dump(), par=par, total_score=total_score)
        for course, total_score, par in courses
    ]


def read_course_with_user_stats(
    session: Session, course_id: int, user_id: int
) -> CourseWithStats | None:

    stmt_course = (
        select(Course)
        .options(selectinload(Course.tracks))
        .where(Course.id == course_id)
    )
    db_course = session.exec(stmt_course).first()
    if not db_course:
        raise HTTPException(404, f"Course id {course_id} not found")

    course_track_count_subq = (
        select(func.count(Track.track_number))
        .where(Track.course_id == course_id)
        .scalar_subquery()
    )

    db_type = session.bind.dialect.name
    if db_type == "sqlite":
        time_diff = (
            func.julianday(func.max(Score.created_at))
            - func.julianday(GameSession.started_at)
        ) * 86400
    else:
        time_diff = func.unix_timestamp(
            func.max(Score.created_at)
        ) - func.unix_timestamp(GameSession.started_at)

    round_totals = (
        select(
            Score.game_session_id,
            func.sum(Score.score).label("round_total"),
            case(
                (time_diff > (6 * 3600), 0),
                (time_diff.is_(None), 0),
                else_=cast(time_diff, Integer),
            ).label("playtime"),
        )
        .join(GameSession, Score.game_session_id == GameSession.id)
        .where(Score.user_id == user_id, Score.course_id == course_id, Score.score > 0)
        .group_by(Score.game_session_id)
        .having(func.count(Score.track_number) == course_track_count_subq)
        .subquery()
    )

    best_per_track = (
        select(func.min(Score.score).label("track_best"))
        .where(Score.user_id == user_id, Score.course_id == course_id, Score.score > 0)
        .group_by(Score.track_number)
        .subquery()
    )
    hypothetical_best_subq = select(
        func.sum(best_per_track.c.track_best)
    ).scalar_subquery()

    best_round_id_subq = (
        select(round_totals.c.game_session_id)
        .order_by(
            round_totals.c.round_total.asc(),
            round_totals.c.game_session_id.desc(),
        )
        .limit(1)
        .scalar_subquery()
    )

    stmt_avg_play_cnt = select(
        func.count(round_totals.c.game_session_id).label("game_count"),
        func.coalesce(func.avg(round_totals.c.round_total), 0).label("avg_score"),
        func.coalesce(func.min(round_totals.c.round_total), 0).label("best_round"),
        func.coalesce(func.sum(round_totals.c.playtime), 0).label("playtime"),
        best_round_id_subq.label("best_round_id"),
        func.coalesce(hypothetical_best_subq, 0).label("hypothetical_best"),
    )
    db_stats = session.exec(stmt_avg_play_cnt).first()
    total_par = sum([track.par for track in db_course.tracks])

    recent_rounds_db = read_game_session_user(session, user_id, None, course_id, 5)

    recent_rounds = [
        GameSessionReadShortWithoutCourse(**game.model_dump(), score=game.user_score)
        for game in recent_rounds_db
    ]

    ret = CourseWithStats(
        **db_course.model_dump(),
        tracks=db_course.tracks,
        total_par=total_par,
        games_played_cnt=db_stats.game_count,
        score_avg=db_stats.avg_score,
        best_round=db_stats.best_round,
        best_round_id=db_stats.best_round_id,
        hypothetical_best=db_stats.hypothetical_best,
        user_recent_rounds=recent_rounds,
        playtime=db_stats.playtime,
    )

    return ret


def read_course_history_user_stats(
    session: Session, course_id: int, user_id: int
) -> CourseWithStats | None:
    stmt_course = (
        select(Course, func.sum(Track.par).label("total_par"))
        .join(Track, Course.id == Track.course_id)
        .where(Course.id == course_id)
    )
    db_course = session.exec(stmt_course).first()

    if not db_course:
        raise HTTPException(404, f"Course id {course_id} not found")

    course_track_count_subq = (
        select(func.count(Track.track_number))
        .where(Track.course_id == course_id)
        .scalar_subquery()
    )

    stmt = (
        select(GameSession, func.sum(Score.score).label("total_score"))
        .join(Score, GameSession.id == Score.game_session_id)
        .where(
            GameSession.course_id == course_id,
            Score.user_id == user_id,
            Score.score > 0,
        )
        .having(func.count(Score.track_number) == course_track_count_subq)
        .group_by(GameSession.id)
        .order_by(GameSession.started_at.asc())
    )
    games = session.exec(stmt).all()

    return CourseStatHistory(
        **db_course[0].model_dump(),
        par=db_course[1],
        user_past_rounds=[
            GameSessionReadStat(**game.model_dump(), score=score)
            for game, score in games
        ],
    )
