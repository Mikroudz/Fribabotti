from sqlmodel import (
    Session,
)
from pydantic import ValidationError
from fastapi import HTTPException

from urllib.parse import parse_qsl

from .model import User, UserCreateTgAuth
from utils.auth import verify_telegram_hash, verify_telegram_hash_webapp

from models.auth.model import TgWebAppAuthData


def create_user(session: Session, new_user) -> User | None:

    db_user = session.get(User, new_user.id)
    if not db_user:
        try:
            db_user = User(
                first_name=new_user.first_name,
                username=new_user.username,
                id=new_user.id,
            )
        except ValidationError as e:
            raise e
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return db_user


def telegram_login(session: Session, data: TgWebAppAuthData | UserCreateTgAuth) -> User:
    if data.type == "TGAUTH":
        valid_user = verify_telegram_hash(data)
    elif data.type == "TGWEBAPP":
        parsed_data = dict(parse_qsl(data.value, keep_blank_values=True))
        print(parsed_data)
        valid_user = verify_telegram_hash_webapp(parsed_data)

    if not valid_user:
        raise HTTPException(status_code=401, detail="Invalid authentication data")

    db_user = session.get(User, valid_user.id)
    # If user does not have username, use first + last
    if valid_user.username == "" or valid_user.username == None:
        valid_user.username = " ".join([valid_user.first_name, valid_user.last_name])
    if db_user:
        user_data = valid_user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
    else:
        db_user = User(**valid_user.model_dump())
    session.add(db_user)
    session.commit()
    return db_user


def read_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)
