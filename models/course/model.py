from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, String
from pydantic import ConfigDict
from models.track.model import Track
from models.game_session.model import GameSession

if TYPE_CHECKING:
    from models.game.model import Game


class CourseBase(SQLModel):
    name: str = Field(sa_type=String(128), max_length=128, min_length=2)
    location: str | None = Field(sa_type=String(128), max_length=128)
    deleted: bool = False


class Course(CourseBase, table=True):
    model_config = ConfigDict(validate_assignment=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    game: Optional["Game"] = Relationship(
        back_populates="courses",
    )
    game_id: Optional[int] = Field(default=None, foreign_key="game.id")
    tracks: List["Track"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={
            "cascade": "all,delete,delete-orphan",
            #      "foreign_keys": "[track.track_number, track.course_id]",
        },
    )
    game_sessions: List[GameSession] = Relationship(
        back_populates="course",
    )


class CourseUpdate(SQLModel):
    name: str | None = None
    location: str | None = None
    deleted: bool | None = None
