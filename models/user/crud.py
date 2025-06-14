from sqlmodel import (
    Session,
)
from pydantic import ValidationError

from .model import User


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
