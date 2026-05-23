import pytest
from decimal import Decimal

from time import sleep
from sqlmodel import Session, select, delete, and_
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import random
from sqlmodel import Session, select

# Replace these imports with the actual paths to your models
from models.game.model import Game
from models.course.model import Course
from models.track.model import Track

# Assuming the router is attached to /courses
ROUTE_PREFIX = "/courses"


def setup_game_in_db(session: Session):
    """Helper function to seed the required Game ID=1"""
    game = session.get(Game, 1)
    if not game:
        game = Game(id=1, name="Disc Golf")  # Adjust fields based on your Game model
        session.add(game)
        session.commit()


def test_course_create(client: TestClient, session: Session):
    # 1. Setup: The endpoint requires Game with ID=1 to exist
    setup_game_in_db(session)

    # 2. Define the payload
    payload = {
        "name": "Maple Hill",
        "location": "Leicester, MA",
        "tracks": [
            {"track_number": 1, "par": 4},
            {"track_number": 2, "par": 3},
            {"track_number": 3, "par": 3},
        ],
    }

    # 3. Act: Send the POST request
    # Note: If you require Auth headers, add them here: client.post(..., headers={"Authorization": "Bearer ..."})
    response = client.post(f"{ROUTE_PREFIX}", json=payload)

    # 4. Assert: Validate API Response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maple Hill"
    assert data["location"] == "Leicester, MA"
    assert len(data["tracks"]) == 3

    # 5. Assert: Validate Database State
    session.expire_all()  # Clear session cache
    db_course = session.exec(select(Course).where(Course.name == "Maple Hill")).first()
    assert db_course is not None
    assert len(db_course.tracks) == 3


def test_course_update_modifies_deletes_and_adds_tracks(
    client: TestClient, session: Session
):
    # 1. Setup: Seed initial Game, Course, and Tracks
    setup_game_in_db(session)

    course = Course(name="Original Course", location="Original Loc", game_id=1)
    session.add(course)
    session.commit()
    session.refresh(course)

    track1 = Track(course_id=course.id, track_number=1, par=3)
    track2 = Track(course_id=course.id, track_number=2, par=4)  # We will delete this
    session.add_all([track1, track2])
    session.commit()

    # 2. Define Update Payload
    # Goals: Change Course Name, Change Track 1 par to 4, Delete Track 2, Add Track 3
    payload = {
        "id": course.id,
        "name": "Updated Course",
        "tracks": [
            {"track_number": 1, "par": 4},  # Modifying existing
            {"track_number": 3, "par": 5},  # Adding new (notice track 2 is missing)
        ],
    }

    # 3. Act: Send PATCH request
    response = client.patch(f"{ROUTE_PREFIX}/{course.id}", json=payload)

    # 4. Assert: Validate API Response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Course"

    # Check that tracks returned by API match our expectations
    returned_tracks = {t["track_number"]: t["par"] for t in data["tracks"]}
    assert len(returned_tracks) == 2
    assert returned_tracks.get(1) == 4  # Updated
    assert returned_tracks.get(2) is None  # Deleted
    assert returned_tracks.get(3) == 5  # Added

    # 5. Assert: Validate Database State (To ensure orphan deletion worked)
    session.expire_all()

    db_tracks = session.exec(select(Track).where(Track.course_id == course.id)).all()

    assert len(db_tracks) == 2
    db_track_dict = {t.track_number: t.par for t in db_tracks}

    assert db_track_dict[1] == 4
    assert 2 not in db_track_dict
    assert db_track_dict[3] == 5
