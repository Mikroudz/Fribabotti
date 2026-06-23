from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session


from models.user_group.crud import (
    read_groups,
    read_group,
    read_group_long,
    read_group_invite,
    invite_join_group,
    create_group,
    edit_group,
    delete_group,
)

from models.user_group.model import (
    UserGroupReadShort,
    UserGroupRead,
    UserGroupReadShort,
    CreateUserGroup,
    UpdateUserGroup,
)


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


@router.get("/{group_id}", response_model=UserGroupRead)
async def get_user_group(
    *, request: Request, session: Session = Depends(get_session), group_id: int
):
    return read_group_long(session, group_id, user_id=request.state.user_id)


@router.post("", response_model=UserGroupRead)
async def group_create(
    *, request: Request, session: Session = Depends(get_session), data: CreateUserGroup
):
    return create_group(
        session,
        group_name=data.name,
        user_id=request.state.user_id,
        notify_groups=False,
    )


@router.delete("/{group_id}")
async def group_del(
    *, request: Request, session: Session = Depends(get_session), group_id: int
):
    return delete_group(session, group_id)


@router.patch("/{group_id}", response_model=UserGroupRead)
async def group_edit(
    *,
    request: Request,
    session: Session = Depends(get_session),
    group_id: int,
    data: UpdateUserGroup,
):
    return edit_group(
        session,
        group_id,
        data=data,
        reset_invite=data.reset_invite,
    )


@router.get("/join/{invite}", response_model=UserGroupReadShort)
async def read_group_invite(
    *, request: Request, session: Session = Depends(get_session), invite: str
):
    return read_group_invite(session, invite)


@router.post("/join/{invite}", response_model=UserGroupReadShort)
async def join_user_group_invite(
    *, request: Request, session: Session = Depends(get_session), invite: str
):
    res = invite_join_group(session, invite, request.state.user_id)
    if res == None:
        raise HTTPException(404, "User does not exist")
    return res
