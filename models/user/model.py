from typing import Optional, List, TYPE_CHECKING, Literal
from datetime import datetime
from pydantic import computed_field, model_validator
from sqlmodel import Field, SQLModel, Relationship

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

    @computed_field
    @property
    def name(self) -> int:
        if self.username == "":
            return self.first_name + self.last_name
        return self.username


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


class UserReadLong(UserBase):
    id: int


class UserCreateNestedUser(SQLModel):
    id: int
    username: str
    first_name: str
    last_name: str


class UserBaseOptionalUsername(UserBase):
    username: str | None = ""


class GroupMemberRead(SQLModel):
    name: str = ""
    id: int
    photo_url: str | None = None


class UserCreate(UserBaseOptionalUsername):
    id: Optional[int] | None


class UserCreateTgAuth(UserBaseOptionalUsername):
    type: Literal["TGAUTH"]

    @computed_field
    @property
    def name(self) -> str:
        return None

    id: Optional[int] | None


class UserCreateTgWebApp(SQLModel):
    type: Literal["TGWEBAPP"]
    query_id: str | None
    user: str | None  # This holds JSON
    auth_date: datetime
    hash: str
    signature: str
