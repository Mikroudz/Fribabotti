from typing import Optional, List, TYPE_CHECKING, Dict, Any
from pydantic import computed_field
from utils.formatting import par_score_format
from sqlmodel import Field, SQLModel, Relationship, text
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from pydantic_extra_types.coordinate import Coordinate

if TYPE_CHECKING:
    from models.game_session.model import GameSession
    from models.track.model import Track
    from models.user.model import User
    from models.score.model import Score


class ThrowBase(SQLModel):
    throw_number: int
    is_penalty: bool = False

    start_lat: float | None = None
    start_lng: float | None = None

    end_lat: float | None = None
    end_lng: float | None = None
    # distance: float = 0.0 TODO: make distance to a calculated field
    # disc: str = ""  # TODO: add table for discs and relation here


class Throw(ThrowBase, table=True):
    __tablename__ = "throw"
    id: Optional[int] = Field(default=None, primary_key=True)

    # Link it directly to the existing score
    score_id: int = Field(foreign_key="score.id", nullable=False)
    score: Optional["Score"] = Relationship(back_populates="throws")


class ThrowReadLong(ThrowBase):
    id: int


class ThrowCreate(SQLModel):
    track_number: int
    game_session_id: int

    start_lat: float | None = None
    start_lng: float | None = None

    end_lat: float | None = None
    end_lng: float | None = None


class ThrowUpdate(SQLModel):
    id: int
    throw_number: int

    start_lat: float | None = None
    start_lng: float | None = None

    end_lat: float | None = None
    end_lng: float | None = None


class ThrowLandingPos(SQLModel):
    lat: float | None = None
    lng: float | None = None
