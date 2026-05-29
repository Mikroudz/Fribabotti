from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session


from models.user.crud import read_user

from models.user_group.model import UserGroupReadShort
from models.user.model import UserReadLong


from .route_deps import token_required_user_id_in_response

router = APIRouter(
    prefix="/profile",
    tags=["user"],
    dependencies=[Depends(token_required_user_id_in_response)],
)


@router.get("", response_model=UserReadLong)
async def register_device(
    *,
    request: Request,
    session: Session = Depends(get_session),
):
    return read_user(session, request.state.user_id)
