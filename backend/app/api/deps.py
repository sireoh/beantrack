"""FastAPI dependencies. Use the `Annotated` aliases at the bottom in route signatures."""

from collections.abc import Iterator
from typing import Annotated, cast

import httpx
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, sessionmaker

from app.clients.b2 import B2Client
from app.clients.discord import DiscordOAuthClient
from app.clients.omdb import OmdbClient
from app.clients.tvmaze import TvMazeClient
from app.core.config import Settings
from app.core.errors import AppError
from app.core.security import TokenCipher
from app.models import User, UserRole
from app.services import auth as auth_service


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_db(request: Request) -> Iterator[Session]:
    factory = cast(sessionmaker[Session], request.app.state.sessionmaker)
    with factory() as db:
        yield db


def get_http_client(request: Request) -> httpx.Client:
    return cast(httpx.Client, request.app.state.http_client)


SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[Session, Depends(get_db)]
HttpClient = Annotated[httpx.Client, Depends(get_http_client)]


def get_tvmaze(http: HttpClient) -> TvMazeClient:
    return TvMazeClient(http)


def get_omdb(http: HttpClient, settings: SettingsDep) -> OmdbClient:
    return OmdbClient(http, settings.omdb_api_key.get_secret_value())


def get_discord(http: HttpClient, settings: SettingsDep) -> DiscordOAuthClient:
    return DiscordOAuthClient(
        http,
        client_id=settings.discord_client_id,
        client_secret=settings.discord_client_secret.get_secret_value(),
        redirect_uri=settings.discord_redirect_uri,
    )


def get_cipher(settings: SettingsDep) -> TokenCipher:
    return TokenCipher(settings.encryption_key.get_secret_value())


def get_current_user(request: Request, db: DbSession, settings: SettingsDep) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    user = auth_service.resolve_session(db, token) if token else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    """401 when logged out (via get_current_user), 403 for anyone who isn't an admin."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user


def get_b2(http: HttpClient, settings: SettingsDep) -> B2Client:
    configured = (
        settings.b2_key_id
        and settings.b2_application_key.get_secret_value()
        and settings.b2_bucket_name
    )
    if not configured:
        raise AppError(
            "Backups are not configured: set B2_KEY_ID, B2_APPLICATION_KEY and B2_BUCKET_NAME"
        )
    return B2Client(
        http,
        key_id=settings.b2_key_id,
        application_key=settings.b2_application_key.get_secret_value(),
        bucket_name=settings.b2_bucket_name,
    )


TvMaze = Annotated[TvMazeClient, Depends(get_tvmaze)]
Omdb = Annotated[OmdbClient, Depends(get_omdb)]
Discord = Annotated[DiscordOAuthClient, Depends(get_discord)]
Cipher = Annotated[TokenCipher, Depends(get_cipher)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
B2 = Annotated[B2Client, Depends(get_b2)]
