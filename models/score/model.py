from typing import Optional, List, TYPE_CHECKING, Dict, Any
from pydantic import computed_field
from utils.formatting import par_score_format
from sqlmodel import Field, SQLModel, Relationship, DateTime
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from models.throw.model import ThrowReadLong
from datetime import datetime
from models.track.model import HoleReadLong
from utils.helpers import utc_now_naive

if TYPE_CHECKING:
    from models.game_session.model import GameSession
    from models.track.model import Track
    from models.user.model import User
    from models.throw.model import Throw


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

    throws: List["Throw"] = Relationship(
        back_populates="score",
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
    )

    created_at: Optional[datetime] = Field(
        default_factory=utc_now_naive,
        sa_type=DateTime(timezone=False),
    )


class ScoreRead(SQLModel):
    user_id: int
    track_number: int
    par: int
    score: int | None = None
    throws: List[ThrowReadLong] = []


class ScoreReadNoThrows(SQLModel):
    track_number: int
    par: int
    score: int | None = None


class CourseScore(SQLModel):
    id: int
    username: str = ""
    photo_url: str | None = None
    total_score: int = 0
    par: int = 0
    scores: List[HoleReadLong] = []


class CourseScoreShort(SQLModel):
    id: int
    username: str = ""
    photo_url: str | None = None
    total_score: int = 0
    par: int = 0
    scores: List[ScoreReadNoThrows] = []


class UpdateScore(SQLModel):
    user_id: int
    game_session_id: int
    track_number: int
    score: int
