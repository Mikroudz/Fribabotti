from sqlmodel import create_engine, SQLModel, Session, Relationship
from models.user.model import User

from models.game_session.model import GameSession

from models.group_chat.model import GroupChat

from models.user_group.model import UserGroup

from models.track.model import Track
from models.score.model import Score

from models.course.model import Course
from models.game.model import Game
from models.links.session_participants_link import SessionParticipantsLink
from models.links.user_group_chat_link import UserGroupChatLink
from models.links.user_group_members_link import UserGroupMembersLink


from dotenv import dotenv_values


secrets = dotenv_values(".env")

sqlite_file_name = "database.db"

db_url = ""

if secrets["DB_TYPE"] == "sqlite":
    db_url = f"sqlite:///{sqlite_file_name}"
elif secrets["DB_TYPE"] == "mysql":
    db_url = f"mysql+pymysql://{secrets['DB_USER']}:{secrets['DB_PASSWORD']}@{secrets['DB_HOST']}/{secrets['DB_DATABASE']}"

engine_args = (
    {"connect_args": {"check_same_thread": False}}
    if secrets["DB_TYPE"] == "sqlite"
    else {"pool_pre_ping": True}
)

engine = create_engine(db_url, pool_size=20, **engine_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
