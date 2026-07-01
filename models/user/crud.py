from sqlmodel import Session, select, func, case, and_, case
from pydantic import ValidationError
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

from .model import User, UserCreateTgAuth, UserCreateGuest, UserReadLong, UserStats
from models.user_group.model import UserGroup
from models.links.session_participants_link import SessionParticipantsLink
from models.game_session.model import GameSession
from utils.auth import verify_telegram_hash, verify_telegram_hash_webapp
from utils.helpers import get_first_available_id

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


def create_guest_user(
    session: Session, guest_data: UserCreateGuest, creator_user_id: int
) -> User:
    db_creator = session.get(User, creator_user_id)
    if not db_creator:
        HTTPException(404, "Invalid user")
    db_group = session.get(UserGroup, guest_data.user_group_id)
    if not db_group:
        HTTPException(404, "Invalid group")
    # we should put guest user outside telegram id range
    guest = User(
        **guest_data.model_dump(exclude="user_group_id"),
        is_guest=True,
        managed_by_user_id=creator_user_id,
        user_groups=[db_group],
        id=get_first_available_id(session, User)
    )
    session.add(guest)
    session.commit()
    session.refresh(guest)
    return guest


def delete_guest_user(session: Session, deleter_id: int, guest_id: int):
    guest_db = session.exec(
        select(User).where(User.id == guest_id, User.managed_by_user_id == deleter_id)
    ).first()
    if not guest_id:
        HTTPException(404, "User does not exist or no permissions to delete")
    session.delete(guest_db)
    session.commit()
    return {"status": "ok"}


def telegram_login(session: Session, data: TgWebAppAuthData | UserCreateTgAuth) -> User:
    if data.type == "TGAUTH":
        valid_user = verify_telegram_hash(data)
    elif data.type == "TGWEBAPP":
        parsed_data = dict(parse_qsl(data.value, keep_blank_values=True))
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


now = datetime.now(timezone.utc).replace(tzinfo=None)

one_month_ago = now - timedelta(days=30)
three_months_ago = now - timedelta(days=90)
start_of_year = datetime(now.year, 1, 1)


def read_user_with_stats(session: Session, user_id: int) -> UserReadLong | None:
    db_type = session.bind.dialect.name
    if db_type == "sqlite":
        playtime_sec = (
            func.julianday(GameSession.ended_at)
            - func.julianday(GameSession.started_at)
        ) * 86400
    elif db_type == "postgresql":
        playtime_sec = func.extract(
            "EPOCH", GameSession.ended_at - GameSession.started_at
        )
    else:
        playtime_sec = func.unix_timestamp(GameSession.ended_at) - func.unix_timestamp(
            GameSession.started_at
        )

    safe_playtime = case(
        (playtime_sec > (6 * 3600), 0),  # Ignore outliers > 6 hours
        (playtime_sec.is_(None), 0),
        else_=playtime_sec,
    )

    # 2. The Main Query
    stmt = (
        select(
            User,
            func.coalesce(func.sum(safe_playtime), 0).label("total_playtime"),
            func.sum(case((GameSession.started_at >= one_month_ago, 1), else_=0)).label(
                "games_last_month"
            ),
            func.sum(
                case((GameSession.started_at >= three_months_ago, 1), else_=0)
            ).label("games_3_months"),
            func.sum(case((GameSession.started_at >= start_of_year, 1), else_=0)).label(
                "games_ytd"
            ),
        )
        .outerjoin(SessionParticipantsLink, SessionParticipantsLink.user_id == User.id)
        .outerjoin(
            GameSession,
            (GameSession.id == SessionParticipantsLink.game_session_id)
            & (GameSession.ended_at.is_not(None)),
        )
        .where(User.id == user_id)
        .group_by(User.id)
    )

    # 3. Execute and unpack the tuple
    result = session.exec(stmt).first()

    if not result:
        return None

    user_obj, total_playtime, g_month, g_3_months, g_ytd = result

    # 4. Return as a clean dictionary or Pydantic model
    return UserReadLong(
        **user_obj.model_dump(),
        stats=UserStats(
            total_playtime=total_playtime,
            games_3_months=g_3_months,
            games_ytd=g_ytd,
            games_last_month=g_month,
        )
    )


def read_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)
