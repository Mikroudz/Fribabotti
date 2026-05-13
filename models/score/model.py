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


class ScoreBase(SQLModel):
    score: int = None

    @computed_field
    @property
    def score_formatted(self) -> str:
        return par_score_format(self.score)


class Score(ScoreBase, table=True):
    __tablename__ = "score"
    __table_args__ = (
        UniqueConstraint("user_id", "track_number", "game_session_id"),
        ForeignKeyConstraint(
            ["track_number", "course_id"],
            ["track.track_number", "track.course_id"],
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    track_number: Optional[int] = Field(default=None, nullable=False)
    course_id: Optional[int] = Field(default=None, nullable=False)
    track: Optional["Track"] = Relationship(back_populates="scores")

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="scores")

    game_session_id: Optional[int] = Field(
        default=None, nullable=False, foreign_key="game_session.id"
    )
    game_session: Optional["GameSession"] = Relationship(back_populates="scores")


class ThrowReadLong(SQLModel):
    start_pos: Coordinate | None = None
    end_pos: Coordinate | None = None
    throw_number: int
    distance: float = 0.0
    disc: str = ""  # TODO: add table for discs and relation here


class HoleReadLong(SQLModel):
    # TODO: each throw
    track_number: int
    par: int
    throws: List[ThrowReadLong]


class CourseScore(SQLModel):
    user_id: int
    course_id: int
    course: List[HoleReadLong]
