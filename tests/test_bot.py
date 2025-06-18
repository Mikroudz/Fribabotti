import pytest
from sqlmodel import select, Session
from pydantic import ValidationError
from telegram import Chat
from datetime import datetime, timedelta
from telegram.ext import ApplicationBuilder, CommandHandler

from models.course.crud import create_course, delete_course, update_course
from models.course.model import Course, CourseUpdate
from models.game.model import Game
from models.game.crud import create_game
from models.track.crud import upsert_track, delete_track
from models.track.model import Track
from main import start


@pytest.fixture()
def bot():
    application = ApplicationBuilder().updater(None).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    return application


def test_first():
    pass
