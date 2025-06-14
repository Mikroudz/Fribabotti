from typing import List
from sqlmodel import Session, select, and_
from pydantic import ValidationError

from .model import Track
from models.course.model import Course


def create_track(
    session: Session, track_number: int, par: int, course_id: int
) -> Track:

    db_course = session.get(Course, course_id)
    if db_course:
        try:
            track = Track(track_number=track_number, par=par, course=db_course)
        except ValidationError as e:
            raise e
        session.add(track)
        session.commit()
        session.refresh(track)
        return track


def upsert_track(
    session: Session, track_number: int, par: int, course_id: int
) -> Track:

    db_course = session.get(Course, course_id)
    if db_course:

        try:
            track = Track(track_number=track_number, par=par, course_id=db_course.id)
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
        select(Track).where(Track.course_id == course_id).order_by(Track.track_number)
    )
    return session.exec(stmt).all()


def read_tracks_as_text_list(session: Session, course_id: int) -> str:
    tracks = read_tracks(session, course_id)
    tracks_list = (
        "\nTrack nr, par\n"
        + "\n".join(
            [f"{track.track_number} {track.par} /del_{track.id}" for track in tracks]
        )
        if len(tracks) > 0
        else "\nAdd first track to course"
    )
    return tracks_list


def delete_track(session: Session, track_id: int):
    db_track = session.get(Track, track_id)
    if db_track:
        session.delete(db_track)
        session.commit()


def update_track(
    session: Session, track_id: int, track_number: int | None, par: int | None
) -> Track:
    db_track = session.get(Track, track_id)
    if db_track:
        db_track.sqlmodel_update(
            Track(track_number=track_number, par=par).model_dump(exclude_unset=True)
        )
        session.commit()
        session.refresh(db_track)
        return db_track
