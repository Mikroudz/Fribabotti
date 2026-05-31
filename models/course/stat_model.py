from models.game_session.model import (
    GameSessionReadShortWithoutCourse,
    GameSessionReadStat,
)
from .model import CourseBase
from models.track.model import TrackRead


class CourseWithStats(CourseBase):
    id: int
    tracks: list[TrackRead] = []
    games_played_cnt: int = 0
    score_avg: float = 0.0
    total_par: int = 0
    best_round: int = 0
    best_round_id: int | None = None
    hypothetical_best: int = 0
    user_recent_rounds: list["GameSessionReadShortWithoutCourse"] = []
    playtime: int = 0


class CourseStatHistory(CourseBase):
    id: int
    par: int = 0
    user_past_rounds: list["GameSessionReadStat"] = []
