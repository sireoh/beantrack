from datetime import timedelta
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_session_token, new_session_token
from app.db.types import utcnow
from app.repositories import sessions as sessions_repo
from app.repositories import users as users_repo
from testing.fakes import FakeUpstream

PROTECTED: list[tuple[str, str, dict[str, Any]]] = [
    ("GET", "/api/tvlist", {}),
    ("POST", "/api/tvlist/add", {"json": {"imdb": "tt0903747"}}),
    ("GET", "/api/movielist", {}),
    ("POST", "/api/movielist/add", {"json": {"imdb": "tt0133093"}}),
    ("GET", "/api/search", {"params": {"type": "tv", "q": "breaking"}}),
    ("GET", "/api/search", {"params": {"type": "movie", "q": "matrix"}}),
    ("GET", "/api/auth/me", {}),
]


@pytest.mark.parametrize(("method", "url", "kwargs"), PROTECTED)
def test_no_cookie_is_401(client: TestClient, method: str, url: str, kwargs: dict[str, Any]) -> None:
    response = client.request(method, url, **kwargs)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(("method", "url", "kwargs"), PROTECTED)
def test_bogus_cookie_is_401(
    app: FastAPI, settings: Settings, method: str, url: str, kwargs: dict[str, Any]
) -> None:
    with TestClient(app, cookies={settings.session_cookie_name: "not-a-real-token"}) as c:
        assert c.request(method, url, **kwargs).status_code == 401


def test_expired_session_is_401(app: FastAPI, settings: Settings, db: Session) -> None:
    now = utcnow()
    users_repo.create_with_lists(db, discord_id="333", username="old", avatar=None, now=now)
    token = new_session_token()
    sessions_repo.create(
        db,
        session_id=hash_session_token(token),
        discord_id="333",
        created_at=now - timedelta(days=31),
        expires_at=now - timedelta(seconds=1),
        device_info=None,
    )
    db.commit()

    with TestClient(app, cookies={settings.session_cookie_name: token}) as c:
        assert c.get("/api/tvlist").status_code == 401


def test_unauthenticated_requests_never_reach_upstream(
    client: TestClient, upstream: FakeUpstream
) -> None:
    client.post("/api/tvlist/add", json={"imdb": "tt0903747"})
    client.get("/api/search", params={"type": "movie", "q": "matrix"})

    assert upstream.requests == []
