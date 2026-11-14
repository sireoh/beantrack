"""Discord OAuth2 login flow and session management."""

import secrets
from datetime import timedelta

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import RedirectResponse

from app.api.deps import Cipher, CurrentUser, DbSession, Discord, SettingsDep
from app.core.config import Settings
from app.core.errors import AppError
from app.schemas.user import UserOut
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_COOKIE = "beantrack_oauth_state"
STATE_COOKIE_PATH = "/api/auth"
STATE_TTL_SECONDS = 600


def _set_session_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        token,
        max_age=int(timedelta(days=settings.session_ttl_days).total_seconds()),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.get("/login", status_code=status.HTTP_302_FOUND)
def login(discord: Discord, settings: SettingsDep) -> RedirectResponse:
    """Redirect the browser to Discord's consent screen."""
    state = secrets.token_urlsafe(24)
    response = RedirectResponse(discord.authorize_url(state), status_code=status.HTTP_302_FOUND)
    # CSRF protection for the OAuth flow: the callback must echo this value back.
    response.set_cookie(
        STATE_COOKIE,
        state,
        max_age=STATE_TTL_SECONDS,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path=STATE_COOKIE_PATH,
    )
    return response


@router.get("/callback", status_code=status.HTTP_302_FOUND)
def callback(
    request: Request,
    db: DbSession,
    discord: Discord,
    cipher: Cipher,
    settings: SettingsDep,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    """Discord redirects here. Creates/updates the user, starts a session, sets the cookie."""
    expected_state = request.cookies.get(STATE_COOKIE)
    if error or not code or not state or not expected_state:
        raise AppError("Discord login was cancelled or is missing parameters")
    if not secrets.compare_digest(state, expected_state):
        raise AppError("Invalid OAuth state")

    token = auth_service.login_with_discord(
        db,
        discord=discord,
        cipher=cipher,
        code=code,
        device_info=request.headers.get("user-agent"),
        session_ttl=timedelta(days=settings.session_ttl_days),
    )
    response = RedirectResponse(settings.frontend_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(STATE_COOKIE, path=STATE_COOKIE_PATH)
    _set_session_cookie(response, token, settings)
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, db: DbSession, settings: SettingsDep) -> Response:
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        auth_service.logout(db, token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(settings.session_cookie_name, path="/")
    return response


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/profile/refresh", response_model=UserOut)
def refresh_profile(
    db: DbSession,
    user: CurrentUser,
    discord: Discord,
    cipher: Cipher,
) -> UserOut:
    """Refresh the current user's profile data from Discord."""
    user = auth_service.refresh_profile(db, user=user, discord=discord, cipher=cipher)
    return UserOut.model_validate(user)
