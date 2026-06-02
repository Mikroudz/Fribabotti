from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session


from models.user.crud import read_user
from models.device_sessions.crud import read_device_sessions_user
from models.device_sessions.model import FrontReadDeviceSession

from models.user.model import UserReadLong


from .route_deps import token_required_user_id_in_response

router = APIRouter(
    prefix="/profile",
    tags=["user"],
    dependencies=[Depends(token_required_user_id_in_response)],
)


@router.get("", response_model=UserReadLong)
async def user_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
):
    return read_user(session, request.state.user_id)


@router.get("/devices", response_model=list[FrontReadDeviceSession])
async def registered_devices(
    *,
    request: Request,
    session: Session = Depends(get_session),
):
    return read_device_sessions_user(
        session, request.state.user_id, filter_unidentified=True
    )
