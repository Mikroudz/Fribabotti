from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, UTC
from pydantic import field_validator
from utils.formatting import datetime_to_pretty
from sqlmodel import Field, SQLModel, Relationship, DateTime
from ..links.session_participants_link import SessionParticipantsLink
from utils.helpers import utc_now_naive

from ..score.model import CourseScore, CourseScoreShort

if TYPE_CHECKING:
    from ..score.model import Score

    from ..course.model import Course
    from ..user_group.model import UserGroup
    from ..user.model import User

CURRENT_TIMEZONE = "Europe/Helsinki"


def strip_timezone(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=UTC)
    return value


class GameSessionBase(SQLModel):

    def started_at_local(self, timezone=None, pretty_print=True) -> datetime | str:
        tz = CURRENT_TIMEZONE if timezone == None else timezone
        return datetime_to_pretty(strip_timezone(self.started_at), tz, pretty_print)

    def ended_at_local(self, timezone=None, pretty_print=True) -> datetime | str:
        tz = CURRENT_TIMEZONE if timezone == None else timezone
        return datetime_to_pretty(strip_timezone(self.ended_at), tz, pretty_print)

    @field_validator("started_at", "ended_at", check_fields=False)
    @classmethod
    def remove_timezone(cls, value):
        return strip_timezone(value)


class GameSession(GameSessionBase, table=True):
    __tablename__ = "game_session"

    id: Optional[int] = Field(default=None, primary_key=True)

    started_at: Optional[datetime] = Field(
        default_factory=utc_now_naive,
        sa_type=DateTime(timezone=False),
    )
    ended_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=False))

    course_id: Optional[int] = Field(
        default=None, foreign_key="course.id", nullable=False
    )
    course: Optional["Course"] = Relationship(back_populates="game_sessions")

    user_group_id: Optional[int] = Field(default=None, foreign_key="user_group.id")
    user_group: Optional["UserGroup"] = Relationship(back_populates="game_sessions")

    participants: List["User"] = Relationship(
        back_populates="game_sessions", link_model=SessionParticipantsLink
    )

    scores: List["Score"] = Relationship(
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
        back_populates="game_session",
    )


class ThrowShortDevice(SQLModel):
    lat: float | None = None
    lng: float | None = None


class HoleReadDevice(SQLModel):
    throws: List[ThrowShortDevice | None] = []
    par: int = 0


# Returns only scores for current user who requested the data
class GameSessionReadDevice(SQLModel):
    holes: List[HoleReadDevice] = []


class GameSessionReadShort(GameSessionBase):
    id: int
    course_id: int
    course: "CourseRead"
    started_at: datetime
    ended_at: datetime | None = None
    par: int = 0
    user_score: int = 0


class GameSessionReadShortWithoutCourse(GameSessionBase):
    id: int
    started_at: datetime
    ended_at: datetime | None = None
    score: int = 0


class GameSessionReadStat(GameSessionBase):
    id: int
    started_at: datetime
    score: int = 0


class GameSessionReadShortWithCourse(SQLModel):
    id: int
    started_at: datetime
    course_name: str = ""
    # this is list of user ID's participating in game for the UI. could be done better
    participants: list[int]


class GameSessionReadLong(GameSessionBase):
    id: int
    course_id: int
    course: "CourseRead"
    started_at: datetime
    ended_at: datetime | None = None
    playtime: int = 0
    user_group_id: int
    user_group: "UserGroupReadShort"
    user_score: CourseScore
    other_scores: List[CourseScoreShort] = []


class GameSessionShort(SQLModel):
    id: int
    name: str = ""


class UpdateGameSession(SQLModel):
    throws: List[List[float]] = []


class DeviceThrowUpdate(SQLModel):
    lat: float | None = None
    lng: float | None = None
    throw_number: int


class DeviceScore(SQLModel):
    throws: list[DeviceThrowUpdate] = []
    # add track/hole number?


class DeviceUpdateGameSession(SQLModel):
    scores: List[DeviceScore] = []
    game_session_id: int | None = None  # not used at the moment


class GameSessionCreate(SQLModel):
    course_id: int
    user_group_id: int


# General stats about user
class GameSessionUserStats(SQLModel):
    playtime: int
    playcount: int


from models.course.model import CourseRead
from ..user_group.model import UserGroupReadShort

GameSessionReadShort.model_rebuild()
GameSessionReadLong.model_rebuild()
