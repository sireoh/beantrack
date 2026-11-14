"""Discord login, app sessions and logout."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.clients.discord import DiscordOAuthClient
from app.core.security import TokenCipher, hash_session_token, new_session_token
from app.db.types import utcnow
from app.models import User
from app.repositories import sessions as sessions_repo
from app.repositories import users as users_repo

MAX_DEVICE_INFO_LENGTH = 512


def login_with_discord(
    db: Session,
    *,
    discord: DiscordOAuthClient,
    cipher: TokenCipher,
    code: str,
    device_info: str | None,
    session_ttl: timedelta,
) -> str:
    """Complete the OAuth callback. Returns the raw session token for the cookie.

    First login creates the user (and their tvlist + movielist); later logins refresh
    the profile and `last_login`. Discord tokens are encrypted before they are stored,
    and only the hash of the session token is persisted.
    """
    tokens = discord.exchange_code(code)
    profile = discord.get_current_user(tokens.access_token)
    now = utcnow()

    user = users_repo.get(db, profile.id)
    if user is None:
        user = users_repo.create_with_lists(
            db, discord_id=profile.id, username=profile.username, avatar=profile.avatar, now=now
        )
    else:
        user.username = profile.username
        user.avatar = profile.avatar
        user.last_login = now

    user.discord_access_token = cipher.encrypt(tokens.access_token)
    user.discord_refresh_token = (
        cipher.encrypt(tokens.refresh_token) if tokens.refresh_token else None
    )
    user.discord_token_expires_at = now + timedelta(seconds=tokens.expires_in)

    sessions_repo.delete_expired_for_user(db, user.discord_id, now)
    raw_token = new_session_token()
    sessions_repo.create(
        db,
        session_id=hash_session_token(raw_token),
        discord_id=user.discord_id,
        created_at=now,
        expires_at=now + session_ttl,
        device_info=device_info[:MAX_DEVICE_INFO_LENGTH] if device_info else None,
    )
    db.commit()
    return raw_token


def resolve_session(db: Session, raw_token: str) -> User | None:
    """The user owning a valid, unexpired session token, or None."""
    session = sessions_repo.get_active(db, hash_session_token(raw_token), utcnow())
    return session.user if session else None


def logout(db: Session, raw_token: str) -> None:
    sessions_repo.delete_by_id(db, hash_session_token(raw_token))
    db.commit()
