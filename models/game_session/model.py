from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, UTC
from pydantic import computed_field, field_validator, field_serializer
from utils.formatting import datetime_to_pretty
from sqlmodel import Field, SQLModel, Relationship, text
from ..links.session_participants_link import SessionParticipantsLink

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

    @computed_field
    @property
    def started_at_local(self, timezone=None, pretty_print=True) -> datetime | str:
        tz = CURRENT_TIMEZONE if timezone == None else timezone
        return datetime_to_pretty(strip_timezone(self.started_at), tz, pretty_print)

    @computed_field
    @property
    def ended_at_local(self, timezone=None, pretty_print=True) -> datetime | str:
        tz = CURRENT_TIMEZONE if timezone == None else timezone
        return datetime_to_pretty(strip_timezone(self.ended_at), tz, pretty_print)


class GameSession(GameSessionBase, table=True):
    __tablename__ = "game_session"

    @field_validator("started_at", "ended_at")
    @classmethod
    def remove_timezone(cls, value):
        return strip_timezone(value)

    @field_serializer("started_at", "ended_at")
    def serialize_started_at(self, val: datetime, _info) -> datetime:
        return strip_timezone(val)

    id: Optional[int] = Field(default=None, primary_key=True)

    started_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        },
    )
    ended_at: Optional[datetime] = Field(
        default=None,
    )
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
