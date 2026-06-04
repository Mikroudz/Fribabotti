from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from models.throw.model import ThrowReadLong, ThrowLandingPos

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func, text

if TYPE_CHECKING:
    from ..course.model import Course
    from ..score.model import Score


class TrackBase(SQLModel):
    par: int = None
    deleted: bool = False
    tee_lat: Optional[float] = None
    tee_lng: Optional[float] = None
    basket_lat: Optional[float] = None
    basket_lng: Optional[float] = None


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


class TrackRead(SQLModel):
    par: int
    track_number: int


class TrackReadUserScore(SQLModel):
    par: int
    track_number: int
    user_avg: float | None = None
    tee_lat: Optional[float] = None
    tee_lng: Optional[float] = None
    basket_lat: Optional[float] = None
    basket_lng: Optional[float] = None


class HoleReadLong(SQLModel):
    track_number: int
    par: int
    score: int | None = None
    throws: List[ThrowReadLong]
    tee_lat: Optional[float] = None
    tee_lng: Optional[float] = None
    basket_lat: Optional[float] = None
    basket_lng: Optional[float] = None


class TrackCreate(SQLModel):
    par: int
    track_number: int


class TrackUpdate(SQLModel):
    id: int
    par: int
    track_number: int


class TrackWithHoleStatistic(TrackBase):
    track_number: int
    throws: list[ThrowLandingPos] = []
