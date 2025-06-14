from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func


class UserGroupChatLink(SQLModel, table=True):
    group_chat_id: int = Field(
        default=None, foreign_key="group_chat.id", primary_key=True
    )
    user_group_id: int = Field(
        default=None, foreign_key="user_group.id", primary_key=True
    )
