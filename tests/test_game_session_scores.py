import pytest
from sqlmodel import select, Session
from pydantic import ValidationError
from telegram import Chat
from datetime import datetime, timedelta

from models.course.crud import create_course, delete_course
from models.course.model import Course
from models.game.model import Game
from models.game.crud import create_game

from models.track.crud import create_track
from models.track.model import Track

from models.game_session.crud import (
    create_game_session,
    end_game_session,
    delete_game_session,
    join_game_session,
)
from models.game_session.model import GameSession

from models.user.crud import create_user
from models.user.model import User

from models.user_group.model import UserGroup
from models.score.crud import upsert_score
from models.score.model import Score

course_location = "hervanta"
course_name = "hervannan frisbeegolf"


@pytest.fixture()
def setup_dummy_data(session: Session):
    game = create_game(session, "testipeli")

    course = create_course(session, course_name, course_location, game.id)
    user = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 1},
        )(),
    )
    user_group = UserGroup(name="testi", members=[user])
    session.add(user_group)
    session.commit()
    session.refresh(user_group)

    track = create_track(session, 1, 2, course.id)

    return game, course, user, user_group, track


def test_create_end_game_session_success(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    create_game_session(session, user.id, course.id, user_group.id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 1
    assert db_sessions[0].ended_at == None

    end_game_session(session, db_sessions[0].id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 1
    assert db_sessions[0].ended_at != None


def test_delete_game_session(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    delete_game_session(session, game_session.id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 0


def test_join_game_session(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 2},
        )(),
    )

    join_game_session(session, user2.id, game_session.id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 1
    assert len(db_sessions[0].participants) == 2


def test_create_score_success(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)

    upsert_score(session, 1, track.track_number, user.id, game_session.id)
    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 1
    assert db_scores[0].score == 1


def test_create_score_unique_another_session_success(
    session: Session, setup_dummy_data
):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    game_session2 = create_game_session(session, user.id, course.id, user_group.id)

    upsert_score(session, 1, track.track_number, user.id, game_session.id)
    upsert_score(session, 2, track.track_number, user.id, game_session2.id)
    session.refresh(game_session)
    session.refresh(game_session2)

    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 2
    assert game_session2.scores[0].score == 2
    assert game_session.scores[0].score == 1


def test_create_score_failure_missing_linked_data(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)

    # missing track
    upsert_score(session, 1, 123, user.id, game_session.id)
    # missing user
    upsert_score(session, 1, track.track_number, 123, game_session.id)
    # missing session
    upsert_score(session, 1, track.track_number, user.id, 123)

    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 0


def test_update_score_success(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)

    upsert_score(session, 1, track.track_number, user.id, game_session.id)
    upsert_score(session, 2, track.track_number, user.id, game_session.id)

    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 1
    assert db_scores[0].score == 2
