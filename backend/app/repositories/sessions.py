from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.models import UserSession


def create(
    db: Session,
    *,
    session_id: str,
    discord_id: str,
    created_at: datetime,
    expires_at: datetime,
    device_info: str | None,
) -> UserSession:
    row = UserSession(
        session_id=session_id,
        discord_id=discord_id,
        created_at=created_at,
        expires_at=expires_at,
        device_info=device_info,
    )
    db.add(row)
    db.flush()
    return row


def get_active(db: Session, session_id: str, now: datetime) -> UserSession | None:
    stmt = (
        select(UserSession)
        .options(joinedload(UserSession.user))
        .where(UserSession.session_id == session_id, UserSession.expires_at > now)
    )
    return db.scalars(stmt).one_or_none()


def delete_by_id(db: Session, session_id: str) -> None:
    db.execute(delete(UserSession).where(UserSession.session_id == session_id))


def delete_expired_for_user(db: Session, discord_id: str, now: datetime) -> None:
    db.execute(
        delete(UserSession).where(
            UserSession.discord_id == discord_id, UserSession.expires_at <= now
        )
    )
