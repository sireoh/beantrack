"""Discord OAuth login, with Discord mocked."""

from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import TokenCipher, hash_session_token
from app.models import MovieList, TvList, UserSession
from testing.conftest import get_user
from testing.fakes import FakeUpstream

DISCORD_ID = "100000000000000001"


def _login(client: TestClient, code: str = "good-code") -> tuple[str, str]:
    """Run /login + /callback. Returns (callback location, session cookie value)."""
    login = client.get("/api/auth/login", follow_redirects=False)
    assert login.status_code == 302
    state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]

    callback = client.get(
        "/api/auth/callback",
        params={"code": code, "state": state},
        headers={"User-Agent": "Mozilla/5.0 (pytest)"},
        follow_redirects=False,
    )
    assert callback.status_code == 302, callback.text
    return callback.headers["location"], callback.cookies.get("beantrack_session", "")


def test_login_redirects_to_discord(client: TestClient, settings: Settings) -> None:
    response = client.get("/api/auth/login", follow_redirects=False)

    assert response.status_code == 302
    url = urlparse(response.headers["location"])
    query = parse_qs(url.query)
    assert url.netloc == "discord.com" and url.path == "/oauth2/authorize"
    assert query["client_id"] == [settings.discord_client_id]
    assert query["redirect_uri"] == [settings.discord_redirect_uri]
    assert query["scope"] == ["identify"]
    assert "beantrack_oauth_state" in response.cookies


def test_first_login_creates_user_lists_and_session(
    client: TestClient, db: Session, settings: Settings
) -> None:
    location, token = _login(client)

    assert location == settings.frontend_url
    assert token

    user = get_user(db, DISCORD_ID)
    assert user.username == "beanfan" and user.avatar == "abc123"
    assert db.scalar(select(func.count()).select_from(TvList)) == 1
    assert db.scalar(select(func.count()).select_from(MovieList)) == 1

    # Discord tokens are encrypted at rest and decrypt back to the originals.
    cipher = TokenCipher(settings.encryption_key.get_secret_value())
    assert user.discord_access_token and user.discord_access_token != "discord-access-plaintext"
    assert cipher.decrypt(user.discord_access_token) == "discord-access-plaintext"
    assert user.discord_refresh_token is not None
    assert cipher.decrypt(user.discord_refresh_token) == "discord-refresh-plaintext"

    # Only the hash of the session token is stored.
    session = db.scalars(select(UserSession)).one()
    assert session.session_id == hash_session_token(token) != token
    assert session.device_info == "Mozilla/5.0 (pytest)"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["discord_id"] == DISCORD_ID
    assert me.json()["avatar_url"] == (
        f"https://cdn.discordapp.com/avatars/{DISCORD_ID}/abc123.png"
    )


def test_session_cookie_is_http_only(client: TestClient) -> None:
    login = client.get("/api/auth/login", follow_redirects=False)
    state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]

    callback = client.get(
        "/api/auth/callback", params={"code": "good-code", "state": state}, follow_redirects=False
    )

    session_cookie = next(
        h for h in callback.headers.get_list("set-cookie") if h.startswith("beantrack_session=")
    )
    assert "HttpOnly" in session_cookie
    assert "samesite=lax" in session_cookie.lower()


def test_second_login_updates_last_login_and_profile(
    client: TestClient, db: Session, upstream: FakeUpstream
) -> None:
    _login(client)
    first = get_user(db, DISCORD_ID)
    created_at, first_login = first.created_at, first.last_login

    upstream.discord_user.username = "beanfan_renamed"
    _login(client)

    user = get_user(db, DISCORD_ID)
    assert user.created_at == created_at
    assert user.last_login > first_login
    assert user.username == "beanfan_renamed"
    # Still exactly one list each, and two sessions (one per login).
    assert db.scalar(select(func.count()).select_from(TvList)) == 1
    assert db.scalar(select(func.count()).select_from(MovieList)) == 1
    assert db.scalar(select(func.count()).select_from(UserSession)) == 2


def test_profile_refresh_updates_avatar_and_username(
    client: TestClient, db: Session, upstream: FakeUpstream
) -> None:
    _login(client)
    upstream.discord_user.username = "beanfan_updated"
    upstream.discord_user.avatar = "new-avatar"

    response = client.post("/api/auth/profile/refresh")

    assert response.status_code == 200
    assert response.json()["username"] == "beanfan_updated"
    assert response.json()["avatar"] == "new-avatar"
    assert get_user(db, DISCORD_ID).avatar == "new-avatar"


def test_callback_rejects_wrong_state(client: TestClient) -> None:
    client.get("/api/auth/login", follow_redirects=False)

    response = client.get(
        "/api/auth/callback", params={"code": "good-code", "state": "forged"}, follow_redirects=False
    )

    assert response.status_code == 400
    assert "beantrack_session" not in response.cookies


def test_callback_rejects_bad_code(client: TestClient) -> None:
    login = client.get("/api/auth/login", follow_redirects=False)
    state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]

    response = client.get(
        "/api/auth/callback", params={"code": "bad-code", "state": state}, follow_redirects=False
    )

    assert response.status_code == 401


def test_logout_revokes_session(client: TestClient, db: Session) -> None:
    _login(client)
    assert client.get("/api/tvlist").status_code == 200

    assert client.post("/api/auth/logout").status_code == 204

    assert db.scalar(select(func.count()).select_from(UserSession)) == 0
    assert client.get("/api/tvlist").status_code == 401



def test_theme_preference_is_saved_on_the_account(client: TestClient) -> None:
    _login(client)
    assert client.get("/api/auth/me").json()["theme"] is None

    response = client.patch("/api/auth/profile/theme", json={"theme": "light"})

    assert response.status_code == 200, response.text
    assert response.json()["theme"] == "light"
    assert client.get("/api/auth/me").json()["theme"] == "light"
    assert client.patch("/api/auth/profile/theme", json={"theme": "pink"}).status_code == 422
