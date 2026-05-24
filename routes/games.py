from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session


from models.game_session.crud import (
    read_game_session_user,
    create_game_session,
    read_game_session,
    read_game_session_long,
    end_game_session,
    delete_game_session,
)
from models.game_session.model import (
    GameSessionCreate,
    GameSessionReadLong,
    GameSessionReadShort,
)
from .route_deps import token_required_user_id_in_response

router = APIRouter(
    prefix="/game_session",
    tags=["game session"],
    dependencies=[Depends(token_required_user_id_in_response)],
)


@router.get("/{game_session_id}", response_model=GameSessionReadLong)
async def game_session_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
    game_session_id: int,
):
    return read_game_session_long(
        session, user_id=request.state.user_id, game_session_id=game_session_id
    )


@router.get("", response_model=List[GameSessionReadShort])
async def game_sessions_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int | None = None,
    limit: int | None = None,
):
    # TODO: add params to read read non active also
    # TODO: create own reading function for api
    return read_game_session_user(
        session,
        user_id=request.state.user_id,
        course_id=course_id,
        limit=limit,
        active=None,
    )


@router.post("", response_model=GameSessionReadLong)
async def game_session_create(
    *,
    request: Request,
    session: Session = Depends(get_session),
    game_session: GameSessionCreate,
):
    created = create_game_session(
        session,
        user_id=request.state.user_id,
        course_id=game_session.course_id,
        user_group_id=game_session.user_group_id,
    )
    return read_game_session_long(
        session, user_id=request.state.user_id, game_session_id=created.id
    )


@router.patch("/{expense_id}", response_model=GameSessionReadLong)
async def game_session_update(
    *,
    request: Request,
    session: Session = Depends(get_session),
    expense_id: int,
    game_session: GameSessionCreate,
):
    return


@router.delete("/{gamesession_id}")
async def game_session_delete(
    *,
    request: Request,
    session: Session = Depends(get_session),
    gamesession_id: int,
):
    # TODO: check if user has permission to delete
    delete_game_session(session, gamesession_id)
    return {"status": "ok"}


# this is separate, but does not need to be. Could be just a part of update
@router.patch("/{gamesession_id}/end", response_model=GameSessionReadLong)
async def game_session_end(
    *,
    request: Request,
    session: Session = Depends(get_session),
    gamesession_id: int,
    close: bool = True,
):
    # TODO: check if user has permission to end
    end_game_session(session, gamesession_id, close=close, read=False)
    return read_game_session_long(
        session, user_id=request.state.user_id, game_session_id=gamesession_id
    )
