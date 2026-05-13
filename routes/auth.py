from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from sqlmodel import Session
from database import get_session
from fastapi.security import HTTPAuthorizationCredentials

from .route_deps import refresh_token_required, access_token_required

from typing import Annotated, Union
from models.user.model import UserRead, UserCreateTgAuth

from models.device_sessions.model import RegisterDeviceData, ReadDeviceSession
from models.device_sessions.crud import (
    register_device_session_by_dev_id,
)

from models.auth.crud import (
    create_session,
    delete_session,
    refresh_session,
)

from models.user.crud import telegram_login


from models.auth.model import TgWebAppAuthData

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/", response_model=ReadDeviceSession)
async def register_device(
    *,
    request: Request,
    session: Session = Depends(get_session),
    data: RegisterDeviceData,
):
    ret = register_device_session_by_dev_id(session, data.device_id)
    return ReadDeviceSession(key=ret.id, username=ret.user.username)


@router.post("/refresh")
async def refresh_token(
    *,
    response: Response,
    session: Session = Depends(get_session),
    token: Annotated[HTTPAuthorizationCredentials, Depends(refresh_token_required)],
):
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = refresh_session(session, user_id, token)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=2592000,
        path=f"/api/v1{router.prefix}/refresh",
    )
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=1800,
    )
    return {"status": "ok"}


@router.post("/telegram", response_model=UserRead)
async def auth_telegram(
    *,
    response: Response,
    session: Session = Depends(get_session),
    auth_data: Union[TgWebAppAuthData, UserCreateTgAuth] = Body(
        ..., discriminator="type"
    ),
):
    user = telegram_login(session, auth_data)
    tokens = create_session(session, user.id)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=2592000,
        path=f"/api/v1{router.prefix}/refresh",
    )
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=1800,
    )

    return user


@router.post("/logout")
async def remove_session(
    *,
    response: Response,
    session: Session = Depends(get_session),
    token: Annotated[HTTPAuthorizationCredentials, Depends(access_token_required)],
):
    delete_session(session, token)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"status": "ok"}
