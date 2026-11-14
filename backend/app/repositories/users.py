from datetime import datetime

from sqlalchemy.orm import Session

from app.models import MovieList, TvList, User


def get(db: Session, discord_id: str) -> User | None:
    return db.get(User, discord_id)


def create_with_lists(
    db: Session, *, discord_id: str, username: str, avatar: str | None, now: datetime
) -> User:
    """Create a user together with their single tvlist and movielist."""
    user = User(
        discord_id=discord_id,
        username=username,
        avatar=avatar,
        created_at=now,
        last_login=now,
    )
    user.tvlist = TvList()
    user.movielist = MovieList()
    db.add(user)
    db.flush()
    return user
