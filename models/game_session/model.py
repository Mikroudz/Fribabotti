from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, text
from ..links.session_participants_link import SessionParticipantsLink

if TYPE_CHECKING:
    from ..score.model import Score

    from ..course.model import Course
    from ..user_group.model import UserGroup
    from ..user.model import User


class GameSessionBase(SQLModel):
    pass


class GameSession(GameSessionBase, table=True):
    __tablename__ = "game_session"

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
