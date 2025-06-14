from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, String

if TYPE_CHECKING:
    from models.course.model import Course


class GameBase(SQLModel):
    name: str | None = Field(sa_type=String(128), max_length=128, min_length=2)


class Game(GameBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    courses: List["Course"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs={"cascade": "save-update,all,delete,delete-orphan"},
    )
