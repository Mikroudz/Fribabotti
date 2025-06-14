from typing import List
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from pydantic import ValidationError

from .model import Course
from models.game.model import Game


def create_course(
    session: Session, name: str, location: str | None, game_id: int
) -> Course:
    db_game = session.get(Game, game_id)
    if db_game:

        try:
            course = Course(name=name, location=location, game=db_game)
        except ValidationError as e:
            raise e
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


def update_course(
    session: Session, course_id: int, name: str | None, location: str | None
) -> Course:
    db_course = session.get(Course, course_id)
    if db_course:
        try:
            course = Course(name=name, location=location)
        except ValidationError as e:
            raise e
        db_course.sqlmodel_update(course.model_dump(exclude_unset=True))
        session.commit()
        session.refresh(course)
        return course


def delete_course(session: Session, course_id: int):
    db_course = session.exec(
        select(Course)
        .options(selectinload(Course.game_sessions))
        .where(Course.id == course_id)
    ).first()
    if db_course:
        if len(db_course.game_sessions) == 0:
            session.delete(db_course)
        else:
            setattr(db_course, "deleted", True)
            session.add(db_course)
        session.commit()


def read_courses(session: Session, game_id: int | None = None) -> List[Course]:
    db_game = None
    if game_id:
        db_game = session.get(Game, game_id)

    stmt = select(Course)
    if db_game:
        stmt = stmt.where(Course.game_id == db_game.id)

    courses = session.exec(stmt).all()
    return courses


def read_course(session: Session, course_id: int) -> Course:
    db_course = session.get(Course, course_id)

    return db_course
