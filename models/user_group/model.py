from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, String

from ..group_chat.model import GroupChat
from ..user.model import User

if TYPE_CHECKING:
    from ..game_session.model import GameSession

from ..links.user_group_chat_link import UserGroupChatLink
from ..links.user_group_members_link import UserGroupMembersLink


class UserGroupBase(SQLModel):
    name: str | None = Field(sa_type=String(128), max_length=128)
    deleted: bool = False


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
