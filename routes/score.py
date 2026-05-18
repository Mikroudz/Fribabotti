from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from fastapi.security import APIKeyHeader
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session

from models.score.crud import upsert_score, read_score
from models.score.model import UpdateScore, ScoreRead
from models.throw.model import ThrowCreate, ThrowUpdate
from models.throw.crud import create_throw, update_throw, remove_throw


from .route_deps import token_required_user_id_in_response

router = APIRouter(
    prefix="/scores",
    tags=["scores"],
    dependencies=[Depends(token_required_user_id_in_response)],
)


@router.post("", response_model=ScoreRead)
async def score_update(
    *,
    request: Request,
    session: Session = Depends(get_session),
    score: UpdateScore,
):
    # TODO: check if user has permission to update the score
    new_score = upsert_score(session, **score.model_dump())
    return read_score(session, new_score.id)


@router.post("/throw", response_model=ScoreRead)
async def throw_create(
    *,
    request: Request,
    session: Session = Depends(get_session),
    throw: ThrowCreate,
):
    return create_throw(session, throw, request.state.user_id)


@router.patch("/throw", response_model=ScoreRead)
async def throw_update(
    *,
    request: Request,
    session: Session = Depends(get_session),
    throw: List[ThrowUpdate],
):
    if isinstance(throw, list):
        # TODO: patch operation inside updathrow
        for t in throw:
            score_id = update_throw(session, t, request.state.user_id)
    else:
        score_id = update_throw(session, throw, request.state.user_id)
    return read_score(session, score_id)


@router.delete("/throw/{throw_id}", response_model=ScoreRead)
async def throw_delete(
    *,
    request: Request,
    session: Session = Depends(get_session),
    throw_id: int,
):
    return remove_throw(session, throw_id, request.state.user_id)
