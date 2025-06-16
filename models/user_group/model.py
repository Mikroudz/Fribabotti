from typing import Optional, List, TYPE_CHECKING, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, String

from ..group_chat.model import GroupChat
from ..user.model import User

if TYPE_CHECKING:
    from ..game_session.model import GameSession

from ..links.user_group_chat_link import UserGroupChatLink
from ..links.user_group_members_link import UserGroupMembersLink
from utils.formatting import create_uuid


def uuid_16_char() -> str:
    return create_uuid(16)


class UserGroupBase(SQLModel):
    name: str | None = Field(sa_type=String(128), max_length=128)
    deleted: bool = False
    notify_groups: bool = False
    invite_code: str = Field(default_factory=uuid_16_char)

    def reset_invite(self):
        setattr(self, "invite_code", uuid_16_char())


class UserGroup(UserGroupBase, table=True):
    __tablename__ = "user_group"

    id: Optional[int] = Field(default=None, primary_key=True)
    chats: List["GroupChat"] = Relationship(
        back_populates="user_groups", link_model=UserGroupChatLink
    )
    members: List["User"] = Relationship(
        back_populates="user_groups", link_model=UserGroupMembersLink
    )
    game_sessions: List["GameSession"] = Relationship(back_populates="user_group")


class UpdateUserGroup(SQLModel):
    name: str | None = None
    deleted: bool | None = None
    notify_groups: bool | None = None
