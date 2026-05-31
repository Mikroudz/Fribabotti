from fastapi import APIRouter, Depends, HTTPException, Response, Body, Request
from fastapi.security import APIKeyHeader
from sqlmodel import Session
from typing import Annotated, Union, List
from database import get_session as get_session

from models.course.model import CourseReadShort, CourseCreate, CourseUpdate
from models.course.stat_model import CourseWithStats, CourseStatHistory
from models.course.crud import (
    read_courses,
    read_course_with_user_stats,
    create_course_with_tracks,
    update_course_with_tracks,
    delete_course,
    read_courses_short,
    read_course_history_user_stats,
)

from models.game.crud import read_games

from .route_deps import token_required_user_id_in_response

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    dependencies=[Depends(token_required_user_id_in_response)],
)


# TODO: make game selection more robust
def get_game_id(session: Session) -> int:
    games = read_games(session)
    game = next((game for game in games if "frisbee" in game.name.lower()))
    if not game:
        raise HTTPException(404, "Game not found (tell administrator)")
    return game.id


@router.get("/{course_id}", response_model=CourseWithStats)
async def course_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
):
    return read_course_with_user_stats(session, course_id, request.state.user_id)


@router.get("/{course_id}/history", response_model=CourseStatHistory)
async def course_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
):
    return read_course_history_user_stats(session, course_id, request.state.user_id)


@router.get("", response_model=List[CourseReadShort])
async def courses_read(*, request: Request, session: Session = Depends(get_session)):

    return read_courses_short(session, get_game_id(session))


@router.post("", response_model=CourseWithStats)
async def course_create(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course: CourseCreate,
):
    cb_course = create_course_with_tracks(session, course, get_game_id(session))
    return read_course_with_user_stats(session, cb_course.id, request.state.user_id)


@router.patch("/{course_id}", response_model=CourseWithStats)
async def course_update(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course: CourseUpdate,
    course_id: int,
):
    update_course_with_tracks(session, course_id, course)
    return read_course_with_user_stats(session, course_id, request.state.user_id)


@router.delete("/{course_id}")
async def course_update(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
):
    delete_course(session, course_id)
    return {"status": "ok"}
