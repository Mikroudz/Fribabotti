from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, APIKeyCookie

from typing import Annotated

from utils.auth import verify_access_token

cookie_refresh = APIKeyCookie(name="refresh_token", auto_error=False)
cookie_access = APIKeyCookie(name="access_token")


def refresh_token_cookie_required(
    token: Annotated[str, Depends(cookie_refresh)] = None,
) -> HTTPAuthorizationCredentials:
    val = HTTPAuthorizationCredentials(scheme="bearer", credentials=token)
    return val


def access_token_cookie_required(
    token: Annotated[str, Depends(cookie_access)] = None,
) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="bearer", credentials=token)


def verify_token(token: HTTPAuthorizationCredentials) -> dict:
    if not token.credentials:
        raise HTTPException(
            status_code=401,
            detail="Token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not token.scheme == "bearer":
        raise HTTPException(
            status_code=401,
            detail="Incorrect authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    verified_jwt = verify_access_token(token.credentials)
    if not verified_jwt:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verified_jwt


def access_token_required(
    token: Annotated[
        HTTPAuthorizationCredentials, Depends(access_token_cookie_required)
    ],
) -> HTTPAuthorizationCredentials:
    return verify_token(token)


def refresh_token_required(
    token: Annotated[
        HTTPAuthorizationCredentials, Depends(refresh_token_cookie_required)
    ],
) -> HTTPAuthorizationCredentials:
    return verify_token(token)


def token_required_user_id(
    token: Annotated[HTTPAuthorizationCredentials, Depends(access_token_required)],
) -> int:
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(user_id) if user_id.isdigit() else user_id


def token_required_user_id_in_response(
    request: Request,
    token: Annotated[HTTPAuthorizationCredentials, Depends(access_token_required)],
) -> None:
    user_id = token_required_user_id(token)
    if user_id:
        request.state.user_id = user_id
