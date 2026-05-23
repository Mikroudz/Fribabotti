from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session


from models.user_group.crud import read_groups

from models.user_group.model import UserGroupReadShort


from .route_deps import token_required_user_id_in_response

router = APIRouter(
    prefix="/groups",
    tags=["user groups"],
    dependencies=[Depends(token_required_user_id_in_response)],
)


@router.get("", response_model=list[UserGroupReadShort])
async def get_user_groups(
    *,
    request: Request,
    session: Session = Depends(get_session),
):
    return read_groups(session, user_id=request.state.user_id)
