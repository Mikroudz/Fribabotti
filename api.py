from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Annotated, Union
from database import get_session

from models.game_session.model import (
    GameSessionRead,
    ThrowRead,
    UpdateGameSession,
    GameSessionShort,
)
from models.score.crud import read_scores, update_game_session
from models.game_session.crud import read_game_session_user

router = APIRouter(prefix="/game", tags=["game"])


@router.get("/{game_session_id}", response_model=GameSessionRead)
async def game_session_read(
    *, request: Request, session: Session = Depends(get_session), game_session_id: int
):
    # TODO: get user id for the device session
    scores = read_scores(session, game_session_id, 145763747)
    out = GameSessionRead()

    for score, track in scores:
        score_num = 0 if score == None else score.score + track.par
        out.holes.append(ThrowRead(throws=[20] * score_num, par=track.par))
    return out


@router.get("/", response_model=list[GameSessionShort])
async def game_session_list(
    *, request: Request, session: Session = Depends(get_session)
):
    # TODO: get user id for the device session
    user_active_games = read_game_session_user(session, 145763747, active=True)
    out = list()

    for game, _ in user_active_games:
        out.append(
            GameSessionShort(
                id=game.id,
                name=f"{game.course.name} {game.started_at_local(None, False).strftime('%Y-%m-%d')}",
            )
        )
    return out


# response {"state": "ok"/"error"}
@router.post("/{session_id}")
async def game_session_update(
    *,
    request: Request,
    session: Session = Depends(get_session),
    data: UpdateGameSession,
    session_id: int,
):
    # TODO: add timestamp from watch: if requests come in incorrect order we can deduce if we should update database values
    return update_game_session(session, session_id, 145763747, data)
