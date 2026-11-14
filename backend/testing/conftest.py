"""Shared fixtures: a temporary SQLite database per test, mocked external APIs, and
helpers that create logged-in users without going through Discord."""

from collections.abc import Callable, Iterator
from datetime import timedelta
from pathlib import Path

import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.security import hash_session_token, new_session_token
from app.db.base import Base
from app.db.types import utcnow
from app.main import create_app
from app.models import User
from app.repositories import sessions as sessions_repo
from app.repositories import users as users_repo
from testing.fakes import OMDB_TEST_KEY, FakeUpstream


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,  # never read a developer's real .env during tests
        data_dir=tmp_path,
        database_name="test.db",
        discord_client_id="test-client-id",
        discord_client_secret="test-client-secret",  # type: ignore[arg-type]
        discord_redirect_uri="http://testserver/api/auth/callback",
        omdb_api_key=OMDB_TEST_KEY,  # type: ignore[arg-type]
        encryption_key=Fernet.generate_key().decode(),  # type: ignore[arg-type]
        cookie_secure=False,  # TestClient talks plain http
        frontend_url="http://localhost:5173/",
    )


@pytest.fixture
def upstream() -> FakeUpstream:
    return FakeUpstream()


@pytest.fixture
def app(settings: Settings, upstream: FakeUpstream) -> FastAPI:
    http = httpx.Client(transport=upstream.transport(), follow_redirects=True)
    application = create_app(settings, http_client=http)
    Base.metadata.create_all(application.state.engine)
    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """An anonymous client (no session cookie)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db(app: FastAPI) -> Iterator[Session]:
    factory: sessionmaker[Session] = app.state.sessionmaker
    with factory() as session:
        yield session


LoginAs = Callable[[str, str], TestClient]


@pytest.fixture
def login_as(app: FastAPI, settings: Settings, db: Session) -> Iterator[LoginAs]:
    """`login_as(discord_id, username)` -> a TestClient carrying a valid session cookie."""
    clients: list[TestClient] = []

    def _login(discord_id: str, username: str) -> TestClient:
        now = utcnow()
        user = users_repo.get(db, discord_id) or users_repo.create_with_lists(
            db, discord_id=discord_id, username=username, avatar=None, now=now
        )
        token = new_session_token()
        sessions_repo.create(
            db,
            session_id=hash_session_token(token),
            discord_id=user.discord_id,
            created_at=now,
            expires_at=now + timedelta(days=1),
            device_info="pytest",
        )
        db.commit()
        test_client = TestClient(app, cookies={settings.session_cookie_name: token})
        clients.append(test_client)
        return test_client

    yield _login
    for c in clients:
        c.close()


@pytest.fixture
def alice(login_as: LoginAs) -> TestClient:
    return login_as("111111111111111111", "alice")


@pytest.fixture
def bob(login_as: LoginAs) -> TestClient:
    return login_as("222222222222222222", "bob")


def get_user(db: Session, discord_id: str) -> User:
    db.expire_all()
    user = users_repo.get(db, discord_id)
    assert user is not None
    return user
