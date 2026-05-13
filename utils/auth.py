from datetime import datetime, timedelta, UTC
from hashlib import sha256
from pydantic import ValidationError
import hmac
import jwt
from jwt.exceptions import InvalidTokenError
import random
import string
from fastapi import HTTPException

from models.auth.model import Token
from models.user.model import UserCreate, UserCreateNestedUser, UserCreateTgAuth

from .env_settings import get_settings

TOKEN_ALGO = "HS256"


def verify_telegram_hash(
    user_data: UserCreateTgAuth,
) -> UserCreate | None:
    data = user_data.model_dump(exclude="type")
    if "auth_date" in data:
        auth_date = verify_timestamp_valid_ts(data["auth_date"])
        if not auth_date:
            raise HTTPException(status_code=401, detail="Telegram auth outdated")
        data["auth_date"] = int(round(auth_date.timestamp()))

    received_hash = data.pop("hash")
    # if "user" in data:
    #    from urllib.parse import unquote

    ##data["user"] = unquote(data["user"])¨

    auth_string = "\n".join(
        [f"{key}={val}" for key, val in sorted(data.items()) if (val)]
    )
    secret_key = sha256(get_settings().telegram_bot_secret.encode("utf-8")).digest()

    calculated_hash = hmac.new(
        secret_key, auth_string.encode("utf-8"), sha256
    ).hexdigest()
    if hmac.compare_digest(calculated_hash, received_hash):
        return UserCreate(**data)
    return None


def verify_telegram_hash_webapp(
    data: dict,
) -> UserCreate | None:

    if "auth_date" in data:
        auth_date = verify_timestamp_valid_ts(data["auth_date"])
        if not auth_date:
            raise HTTPException(status_code=401, detail="Telegram auth outdated")
        data["auth_date"] = int(round(auth_date.timestamp()))

    received_hash = data.pop("hash")
    auth_string = "\n".join([f"{key}={val}" for key, val in sorted(data.items())])
    secret_key = hmac.new(
        "WebAppData".encode(),
        get_settings().telegram_bot_secret.encode("utf-8"),
        sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key, auth_string.encode("utf-8"), sha256
    ).hexdigest()

    if hmac.compare_digest(calculated_hash, received_hash):
        try:
            nested_user_json = UserCreateNestedUser.model_validate_json(data["user"])
        except ValidationError:
            print("invalid user data", data["user"])
            return None
        validated_user = UserCreate(
            **nested_user_json.model_dump(),
            hash=received_hash,
            auth_date=data.get("auth_date"),
        )
        return validated_user
    return None


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(
        to_encode, get_settings().token_secret_key, algorithm=TOKEN_ALGO
    )
    return jwt_token


def create_access_refresh_tokens(
    user_id: int | str, session_id: str, index: int
) -> Token:

    sub_data = {"sub": str(user_id), "session": session_id, "index": index}
    refresh_token = create_token(
        data=sub_data,
        expires_delta=timedelta(days=30),
    )
    access_token = create_token(data=sub_data, expires_delta=timedelta(minutes=30))
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, get_settings().token_secret_key, algorithms=[TOKEN_ALGO]
        )
        username: str = payload.get("sub")
        if not username:
            return None
        return payload
    except InvalidTokenError as e:
        return None


def verify_timestamp_valid_ts(
    date: str | datetime, delta: timedelta = timedelta(days=1)
) -> datetime | None:
    if type(date) in [str, int]:
        past_time = datetime.fromtimestamp(float(date), UTC)
    else:
        past_time = date

    current_time = datetime.now(UTC)

    if past_time + delta < current_time:
        return None
    return past_time


def create_uuid(len: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=len))
