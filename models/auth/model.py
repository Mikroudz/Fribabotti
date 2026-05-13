from pydantic import BaseModel
from typing import Optional, Literal
from sqlmodel import Field, SQLModel, Relationship, text
from datetime import datetime


class SessionTokenBase(SQLModel):
    counter: int = 0


class SessionToken(SessionTokenBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, sa_column_kwargs={"unique": True})
    last_seen: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": text("CURRENT_TIMESTAMP"),
            "server_default": text("CURRENT_TIMESTAMP"),
        },
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        },
    )


class SessionTokenCreate(SessionTokenBase):
    session_id: str
    token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TgWebAppAuthData(BaseModel):
    type: Literal["TGWEBAPP"]
    value: str
