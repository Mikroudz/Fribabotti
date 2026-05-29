from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Session, select, delete, and_, func
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from utils.auth import (
    create_access_refresh_tokens,
    create_uuid,
    verify_timestamp_valid_ts,
)
from fastapi import HTTPException

from .model import Token, SessionToken


def refresh_session(
    session: Session, user_id: int | str, token: HTTPAuthorizationCredentials = None
) -> Token:
    if not token:
        raise HTTPException(
            status_code=401,
            detail="token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = token.get("session")
    token_index = token.get("index")
    timestamp_valid = verify_timestamp_valid_ts(token.get("exp"))
    valid = all(
        [
            timestamp_valid != None,
            session_id,
            (token_index != None),
        ]
    )
    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Refresh token outdated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_session = session.exec(
        select(SessionToken).where(SessionToken.session_id == session_id)
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=401,
            detail="No active session found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_index != db_session.counter:
        raise HTTPException(
            status_code=401,
            detail="Refresh token counter incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        token_index = token_index + 1 if token_index < 65535 else 0
        db_session.counter = token_index
    session.add(db_session)
    session.commit()
    return create_access_refresh_tokens(user_id, session_id, token_index)


def create_session(session: Session, user_id: int | str) -> Token:
    # User id is validated/created by telegram_auth endpoint so no need to validate here
    token_index = 0
    session_id = create_uuid(8)
    db_session = SessionToken(counter=0, session_id=session_id)
    session.add(db_session)
    session.commit()

    return create_access_refresh_tokens(user_id, session_id, token_index)


def session_get(session: Session, val: str):
    db_session = session.exec(
        select(SessionToken).where(SessionToken.session_id == val)
    ).first()
    return db_session


def delete_session(session: Session, token: HTTPAuthorizationCredentials = None):
    if token:
        session_id = token.get("session")
        if session_id:
            session.exec(
                delete(SessionToken).where(SessionToken.session_id == session_id)
            )
            session.commit()


def clear_expired(session: Session):
    delta = datetime.now() - timedelta(days=30)
    stmt = delete(SessionToken).where(SessionToken.created_at < delta)
    session.exec(stmt)
