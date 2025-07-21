import pytest
from sqlmodel import select, Session
from pydantic import ValidationError
from telegram import Chat
from datetime import datetime, timedelta

from models.course.crud import create_course, delete_course, update_course
from models.course.model import Course, CourseUpdate
from models.game.model import Game
from models.game.crud import create_game
from models.track.crud import upsert_track, delete_track
from models.track.model import Track


def test_create_course_success(session: Session):
    game = create_game(session, "testipeli")
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    create_course(session, name, loc, game.id)
    db_courses = session.exec(select(Course)).all()
    assert len(db_courses) == 1
    assert db_courses[0].location == loc
    assert db_courses[0].name == name


def test_create_course_failure_no_game(session: Session):
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    create_course(session, name, loc, 0)
    db_courses = session.exec(select(Course)).all()
    assert len(db_courses) == 0


def test_create_course_failure_name_missing(session: Session):
    game = create_game(session, "testipeli")

    loc = "hervanta"
    name = ""
    with pytest.raises(ValidationError):
        create_course(session, name, loc, game.id)
    db_courses = session.exec(select(Course)).all()
    assert len(db_courses) == 0


def test_update_course_success(session: Session):
    game = create_game(session, "testipeli")
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    course = create_course(session, name, loc, game.id)

    # Update only name
    update_course(session, course.id, CourseUpdate(name="testi"))
    course = session.get(Course, course.id)
    assert course.name == "testi"
    assert course.location == loc

    # updat only location
    update_course(session, course.id, CourseUpdate(location="paikka"))
    course = session.get(Course, course.id)
    assert course.name == "testi"
    assert course.location == "paikka"

    # Update both location and name
    update_course(session, course.id, CourseUpdate(location="kemi", name="rata"))
    course = session.get(Course, course.id)
    assert course.name == "rata"
    assert course.location == "kemi"


def test_delete_course_cascade_success(session: Session):
    game = create_game(session, "testipeli")
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    course = create_course(session, name, loc, game.id)
    upsert_track(session, 1, 2, course.id)

    delete_course(session, course.id)

    db_tracks = session.exec(select(Track)).all()
    assert len(db_tracks) == 0, "Cascade removes tracks"
    db_courses = session.exec(select(Course)).all()
    assert len(db_courses) == 0


def test_create_track_with_upsert_success(session: Session):
    game = create_game(session, "testipeli")
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    course = create_course(session, name, loc, game.id)
    upsert_track(session, 1, 2, course.id)
    db_tracks = session.exec(select(Track)).all()
    assert len(db_tracks) == 1
    assert db_tracks[0].par == 2
    assert db_tracks[0].track_number == 1


def test_update_track_with_upsert_success(session: Session):
    game = create_game(session, "testipeli")
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    course = create_course(session, name, loc, game.id)
    upsert_track(session, 1, 2, course.id)
    upsert_track(session, 1, 3, course.id)

    db_tracks = session.exec(select(Track)).all()
    assert len(db_tracks) == 1
    assert db_tracks[0].par == 3
    assert db_tracks[0].track_number == 1


def test_create_track_failure_no_course(session: Session):
    upsert_track(session, 1, 2, 0)
    db_tracks = session.exec(select(Track)).all()
    assert len(db_tracks) == 0


def test_delete_track_success(session: Session):
    game = create_game(session, "testipeli")
    loc = "hervanta"
    name = "hervannan frisbeegolf"
    course = create_course(session, name, loc, game.id)
    upsert_track(session, 1, 2, course.id)
    delete_track(session, 1, course.id)
    db_tracks = session.exec(select(Track).where(Track.deleted == False)).all()
    assert len(db_tracks) == 0
