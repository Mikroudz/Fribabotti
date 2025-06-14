from typing import List
from sqlmodel import Session, select
from pydantic import ValidationError

from .model import Game


def create_game(session: Session, name: str) -> Game:

    try:
        game = Game(name=name)
    except ValidationError as e:
        raise e
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def read_games(session: Session) -> List[Game]:

    stmt = select(Game)
    games = session.exec(stmt).all()
    return games
