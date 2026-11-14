from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utcnow
from app.models.enums import UserRole, user_role_column_type

if TYPE_CHECKING:
    from app.models.lists import MovieList, TvList


class User(Base):
    __tablename__ = "users"

    discord_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    username: Mapped[str] = mapped_column(String(64))
    avatar: Mapped[str | None] = mapped_column(String(128))  # Discord avatar hash
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    last_login: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    role: Mapped[UserRole] = mapped_column(
        user_role_column_type(), default=UserRole.USER, server_default=UserRole.USER.value
    )

    # Discord OAuth tokens, Fernet-encrypted with ENCRYPTION_KEY. Never stored in plaintext.
    discord_access_token: Mapped[str | None] = mapped_column(Text)
    discord_refresh_token: Mapped[str | None] = mapped_column(Text)
    discord_token_expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    sessions: Mapped[list[UserSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    tvlist: Mapped[TvList] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    movielist: Mapped[MovieList] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class UserSession(Base):
    """An app login session. `session_id` is the SHA-256 hash of the cookie token."""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    discord_id: Mapped[str] = mapped_column(
        ForeignKey("users.discord_id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    device_info: Mapped[str | None] = mapped_column(String(512))  # User-Agent

    user: Mapped[User] = relationship(back_populates="sessions")
