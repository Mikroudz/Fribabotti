from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from fastapi.security import APIKeyHeader
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

from models.device_sessions.crud import (
    get_user_id_from_device,
)

router = APIRouter(prefix="/game", tags=["game"])

device_token_header = APIKeyHeader(name="X-Device-Token", auto_error=True)


def get_user_id_device(
    token: str = Depends(device_token_header), session: Session = Depends(get_session)
) -> int:
    return get_user_id_from_device(session, token)


@router.get("/{game_session_id}", response_model=GameSessionRead)
async def game_session_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
    game_session_id: int,
    user_id: int = Depends(get_user_id_device),
):
    scores = read_scores(session, game_session_id, user_id)
    out = GameSessionRead()

    for score, track in scores:
        score_num = 0 if score == None else score.score + track.par
        out.holes.append(ThrowRead(throws=[20] * score_num, par=track.par))
    return out


@router.get("/", response_model=list[GameSessionShort])
async def game_session_list(
    *,
    request: Request,
    session: Session = Depends(get_session),
    user_id: int = Depends(get_user_id_device),
):
    user_active_games = read_game_session_user(session, user_id, active=True)
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
    user_id: int = Depends(get_user_id_device),
):
    # TODO: add timestamp from watch: if requests come in incorrect order we can deduce if we should update database values
    return update_game_session(session, session_id, user_id, data)
