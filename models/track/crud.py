from typing import List
from sqlmodel import Session, select, and_, func, text
from pydantic import ValidationError

from .model import Track
from models.course.model import Course
from models.throw.model import Throw
from models.score.model import Score


def upsert_track(
    session: Session, track_number: int, par: int, course_id: int
) -> Track:

    db_course = session.get(Course, course_id)
    if db_course:

        try:
            track = Track(
                track_number=track_number,
                par=par,
                course_id=db_course.id,
                deleted=False,
            )
        except ValidationError as e:
            raise e
        stmt = select(Track).where(
            and_(track_number == Track.track_number, course_id == Track.course_id)
        )
        db_track = session.exec(stmt).first()
        if db_track:
            db_track.sqlmodel_update(track.model_dump(exclude_unset=True))
            session.commit()
            session.refresh(db_track)
            return db_track
        else:
            session.add(track)
            session.commit()
            session.refresh(track)
            return track


def read_tracks(session: Session, course_id: int) -> List[Track]:
    stmt = (
        select(Track)
        .where(and_(Track.course_id == course_id, Track.deleted == False))
        .order_by(Track.track_number)
    )
    return session.exec(stmt).all()


def read_track(session: Session, track_number: int, course_id: int) -> List[Track]:
    return session.exec(
        select(Track).where(
            and_(
                Track.track_number == track_number,
                Track.course_id == course_id,
                Track.deleted == False,
            )
        )
    ).first()


def read_tracks_as_text_list(session: Session, course_id: int) -> str:
    tracks = read_tracks(session, course_id)
    tracks_list = (
        "\nTrack nr, par\n"
        + "\n".join(
            [
                f"{track.track_number} {track.par} /del_{track.track_number}"
                for track in tracks
            ]
        )
        if len(tracks) > 0
        else "\nAdd first track to course"
    )
    return tracks_list


def delete_track(session: Session, track_number: int, course_id: int):
    db_track = read_track(session, track_number, course_id)
    if db_track:
        setattr(db_track, "deleted", True)
        session.commit()


def recalculate_track_gps(session: Session, course_id: int):
    tee_stmt = (
        select(
            Score.track_number,
            func.avg(Throw.start_lat).label("avg_lat"),
            func.avg(Throw.start_lng).label("avg_lng"),
        )
        .join(Score, Score.id == Throw.score_id)
        .where(
            Score.course_id == course_id,
            Throw.throw_number == 1,
        )
        .group_by(Score.track_number)
    )
    tee_coords = session.exec(tee_stmt).all()
    tee_map = {row[0]: (row[1], row[2]) for row in tee_coords}

    max_throws_subq = (
        select(Throw.score_id, func.max(Throw.throw_number).label("max_throw"))
        .group_by(Throw.score_id)
        .subquery()
    )

    basket_stmt = (
        select(
            Score.track_number,  # NOTE: on last throw we use only start position. Not sure yet if this is a good idea but we'll see about that
            func.avg(Throw.start_lat).label("basket_lat"),
            func.avg(Throw.start_lng).label("basket_lng"),
        )
        .join(
            max_throws_subq,
            (Throw.score_id == max_throws_subq.c.score_id)
            & (Throw.throw_number == max_throws_subq.c.max_throw),
        )
        .join(Score, Score.id == Throw.score_id)
        .where(Score.course_id == course_id)
        .group_by(Score.track_number)
    )
    basket_results = session.exec(basket_stmt).all()
    basket_map = {row[0]: (row[1], row[2]) for row in basket_results}
    tracks = session.exec(select(Track).where(Track.course_id == course_id)).all()

    for track in tracks:
        if track.track_number in tee_map:
            track.tee_lat = tee_map[track.track_number][0]
            track.tee_lng = tee_map[track.track_number][1]

        if track.track_number in basket_map:
            track.basket_lat = basket_map[track.track_number][0]
            track.basket_lng = basket_map[track.track_number][1]

        session.add(track)

    session.commit()
