"""Login extras: returning to the page the user came from, and the client IP on sessions."""

import ipaddress
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.client_ip import client_ip
from app.core.config import Settings
from app.models import UserSession


def _login(client: TestClient, *, next_path: str | None = None, headers: dict[str, str] | None = None) -> str:
    params = {"next": next_path} if next_path is not None else {}
    login = client.get("/api/auth/login", params=params, follow_redirects=False)
    state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]
    callback = client.get(
        "/api/auth/callback",
        params={"code": "good-code", "state": state},
        headers=headers or {},
        follow_redirects=False,
    )
    assert callback.status_code == 302, callback.text
    return callback.headers["location"]


# --- return to the page after login ---------------------------------------------------


def test_login_returns_to_the_requested_page(client: TestClient, settings: Settings) -> None:
    location = _login(client, next_path="/discover/tv")
    assert location == "http://localhost:5173/discover/tv"  # settings.frontend_url + path


@pytest.mark.parametrize(
    "unsafe", ["https://evil.example/", "//evil.example/", "/\\evil.example", "discover/tv"]
)
def test_unsafe_next_values_fall_back_to_the_frontend(
    client: TestClient, settings: Settings, unsafe: str
) -> None:
    assert _login(client, next_path=unsafe) == settings.frontend_url


def test_next_is_used_only_once(client: TestClient, settings: Settings) -> None:
    _login(client, next_path="/discover/movies")
    assert _login(client) == settings.frontend_url


# --- client IP ---------------------------------------------------------------------------

LOCAL = [ipaddress.ip_network("127.0.0.1/32"), ipaddress.ip_network("172.16.0.0/12")]


def test_untrusted_peer_headers_are_ignored() -> None:
    assert client_ip("203.0.113.9", "1.2.3.4", "5.6.7.8", LOCAL) == "203.0.113.9"


def test_trusted_proxy_chain_is_read_right_to_left() -> None:
    # A client prepended a fake hop; the proxies appended the real one, then their own.
    chain = "6.6.6.6, 198.51.100.7, 172.18.0.1"
    assert client_ip("172.18.0.5", chain, None, LOCAL) == "198.51.100.7"


def test_x_real_ip_is_used_without_x_forwarded_for() -> None:
    assert client_ip("127.0.0.1", None, "198.51.100.7", LOCAL) == "198.51.100.7"
    assert client_ip("127.0.0.1", None, "not-an-ip", LOCAL) == "127.0.0.1"


def test_star_trusts_every_peer() -> None:
    assert client_ip("203.0.113.9", "198.51.100.7", None, None) == "198.51.100.7"


def test_forwarded_allow_ips_must_be_valid(settings: Settings) -> None:
    with pytest.raises(ValueError):
        Settings.model_validate({**settings.model_dump(), "forwarded_allow_ips": "not-an-ip"})
    ok = Settings.model_validate({**settings.model_dump(), "forwarded_allow_ips": "10.0.0.0/8, ::1"})
    assert ok.trusted_proxies == [ipaddress.ip_network("10.0.0.0/8"), ipaddress.ip_network("::1")]


def _session_ip(db: Session) -> str | None:
    db.expire_all()
    return db.scalars(select(UserSession.ip_address)).one()


def test_session_stores_the_ip_from_a_trusted_proxy(app: FastAPI, db: Session) -> None:
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        _login(client, headers={"X-Forwarded-For": "198.51.100.7"})
    assert _session_ip(db) == "198.51.100.7"


def test_session_ignores_forwarded_headers_from_other_peers(app: FastAPI, db: Session) -> None:
    with TestClient(app, client=("203.0.113.9", 50000)) as client:
        _login(client, headers={"X-Forwarded-For": "198.51.100.7", "X-Real-IP": "198.51.100.8"})
    assert _session_ip(db) == "203.0.113.9"
