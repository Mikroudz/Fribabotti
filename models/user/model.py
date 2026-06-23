from typing import Optional, List, TYPE_CHECKING, Literal
from datetime import datetime
from pydantic import computed_field
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
    is_guest: bool = False

    @computed_field
    @property
    def name(self) -> str:
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
    managed_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    guests: List["User"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "User.id==User.managed_by_user_id",
            "remote_side": "User.id",
        }
    )


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


class UserCreateGuest(SQLModel):
    username: str
    # for now we require group. Later might not need
    user_group_id: int


class UserCreateTgAuth(UserBaseOptionalUsername):
    type: Literal["TGAUTH"]

    @computed_field
    @property
    def name(self) -> None:
        return None

    id: Optional[int] | None


class UserCreateTgWebApp(SQLModel):
    type: Literal["TGWEBAPP"]
    query_id: str | None
    user: str | None  # This holds JSON
    auth_date: datetime
    hash: str
    signature: str
