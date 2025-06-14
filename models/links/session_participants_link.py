from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func

if TYPE_CHECKING:
    from ..user.model import User


class SessionParticipantsLink(SQLModel, table=True):
    game_session_id: int = Field(
        default=None, foreign_key="game_session.id", primary_key=True
    )
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
