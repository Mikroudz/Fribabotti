import pytest

from fastapi.testclient import TestClient
from fastapi import Request
from httpx import Cookies

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from models.auth.crud import create_session
from database import get_session
from main import app


def create_cookie(session: Session, user_id: int = 1) -> Cookies:
    token = create_session(session, user_id)

    cookie = Cookies()
    cookie.set(
        name="access_token",
        value=f"{token.access_token}",
    )
    return cookie


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


@app.middleware("http")
async def mock_user_id_middleware(request: Request, call_next):
    request.state.user_id = 1  # Fake user ID for testing
    return await call_next(request)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, cookies=create_cookie(session))
    client.base_url = str(client.base_url) + "/api/v1"
    yield client
    app.dependency_overrides.clear()
