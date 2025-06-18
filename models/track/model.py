from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, text

if TYPE_CHECKING:
    from ..course.model import Course
    from ..score.model import Score


class TrackBase(SQLModel):
    par: int = None
    deleted: bool = False


class Track(TrackBase, table=True):
    __tablename__ = "track"
    __table_args__ = (
        PrimaryKeyConstraint(
            "track_number",
            "course_id",
        ),
        UniqueConstraint("course_id", "track_number"),
    )
    track_number: int = Field(primary_key=True, nullable=False)

    course_id: Optional[int] = Field(
        default=None, foreign_key="course.id", primary_key=True, nullable=False
    )
    course: Optional["Course"] = Relationship(back_populates="tracks")
    scores: List["Score"] = Relationship(back_populates="track")
