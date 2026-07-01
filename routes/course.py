from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from typing import List
from database import get_session as get_session
from fastapi_cache.decorator import cache

from models.course.model import (
    CourseReadShort,
    CourseCreate,
    CourseUpdate,
    CourseWeather,
)
from models.course.stat_model import CourseWithStats, CourseStatHistory
from models.course.crud import (
    read_course_with_user_stats,
    create_course_with_tracks,
    update_course_with_tracks,
    delete_course,
    read_courses_short,
    read_course_history_user_stats,
    read_course_location,
)

from models.game.crud import read_games

from models.track.model import TrackWithHoleStatistic
from models.throw.crud import get_hole_throws_history
from utils.fetchweather import get_current_fmi_weather

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
async def course_read_single(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
):
    return read_course_with_user_stats(session, course_id, request.state.user_id)


@router.get("/{course_id}/weather", response_model=CourseWeather)
@cache(expire=3600)
async def course_weathr(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
):
    loc = read_course_location(session, course_id)
    if loc == None or loc[0] == None:
        return CourseWeather(id=course_id, timestamp=0)
    lat, lng = loc
    weather = await get_current_fmi_weather(lat, lng)
    if "error" in weather:
        raise HTTPException(404, weather["error"])
    setattr(weather, "id", course_id)
    return weather


@router.get("/{course_id}/history", response_model=CourseStatHistory)
async def course_read_history(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
    limit: int = 50,
):
    return read_course_history_user_stats(
        session, course_id, request.state.user_id, limit=limit
    )


@router.get(
    "/{course_id}/history/{track_number}", response_model=TrackWithHoleStatistic
)
async def course_read(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
    track_number: int,
):
    return get_hole_throws_history(
        session,
        course_id=course_id,
        user_id=request.state.user_id,
        track_number=track_number,
    )


@router.get("", response_model=List[CourseReadShort])
async def courses_read(*, request: Request, session: Session = Depends(get_session)):

    return read_courses_short(
        session, get_game_id(session), user_id=request.state.user_id
    )


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
async def course_delete(
    *,
    request: Request,
    session: Session = Depends(get_session),
    course_id: int,
):
    delete_course(session, course_id)
    return {"status": "ok"}
