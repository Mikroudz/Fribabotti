from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func


class UserGroupMembersLink(SQLModel, table=True):
    user_group_id: int = Field(
        default=None, foreign_key="user_group.id", primary_key=True
    )
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
