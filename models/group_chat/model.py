from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, String

if TYPE_CHECKING:
    from models.user_group.model import UserGroup

from models.links.user_group_chat_link import UserGroupChatLink


class GroupChatBase(SQLModel):
    __tablename__ = "group_chat"
    name: str | None = ""


class GroupChat(GroupChatBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    user_groups: List["UserGroup"] = Relationship(
        back_populates="chats",
        link_model=UserGroupChatLink,
    )
