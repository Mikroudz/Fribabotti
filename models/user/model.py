from typing import Optional, List, TYPE_CHECKING, Dict, Any, Literal
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func

from ..links.user_group_members_link import UserGroupMembersLink
from ..links.session_participants_link import SessionParticipantsLink

if TYPE_CHECKING:
    from ..user_group.model import UserGroup
    from ..game_session.model import GameSession
    from ..score.model import Score
    from ..device_sessions.model import DeviceSession


class UserBase(SQLModel):
    first_name: str | None = ""
    username: str | None = ""
    last_name: Optional[str] | None = ""
    photo_url: Optional[str | None] = None
    auth_date: datetime | None = None
    hash: str | None = ""


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

    device_sessions: List["DeviceSession"] = Relationship(back_populates="user")


class UserRead(UserBase):
    id: int


class UserCreateNestedUser(SQLModel):
    id: int
    username: str
    first_name: str
    last_name: str


class UserBaseOptionalUsername(UserBase):
    username: str | None = ""


class UserCreate(UserBaseOptionalUsername):
    id: Optional[int] | None


class UserCreateTgAuth(UserBaseOptionalUsername):
    type: Literal["TGAUTH"]
    id: Optional[int] | None


class UserCreateTgWebApp(SQLModel):
    type: Literal["TGWEBAPP"]
    query_id: str | None
    user: str | None  # This holds JSON
    auth_date: datetime
    hash: str
    signature: str
