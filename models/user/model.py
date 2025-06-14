from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func

from ..links.user_group_members_link import UserGroupMembersLink
from ..links.session_participants_link import SessionParticipantsLink


if TYPE_CHECKING:
    from ..user_group.model import UserGroup
    from ..game_session.model import GameSession
    from ..score.model import Score


class UserBase(SQLModel):

    first_name: str | None = ""
    username: str | None = ""


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_groups: List["UserGroup"] = Relationship(
        back_populates="members",
        link_model=UserGroupMembersLink,
    )
    game_sessions: List["GameSession"] = Relationship(
        back_populates="participants",
        link_model=SessionParticipantsLink,
    )
    scores: List["Score"] = Relationship(back_populates="user")
