from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Episode, TvList, TvShow, UserTvShow, WatchStatus


def get_for_user(db: Session, discord_id: str) -> TvList | None:
    """The user's list with every entry, its show and current episode eagerly loaded."""
    stmt = (
        select(TvList)
        .where(TvList.discord_id == discord_id)
        .options(
            selectinload(TvList.entries).selectinload(UserTvShow.show),
            selectinload(TvList.entries).selectinload(UserTvShow.current_episode),
        )
    )
    return db.scalars(stmt).one_or_none()


def get_entry(db: Session, tvlist_id: str, imdb: str) -> UserTvShow | None:
    return db.get(UserTvShow, (tvlist_id, imdb))


def add_entry(
    db: Session,
    *,
    tvlist: TvList,
    show: TvShow,
    status: WatchStatus,
    current_episode: Episode | None,
    now: datetime,
) -> UserTvShow:
    entry = UserTvShow(
        tvlist_id=tvlist.tvlist_id,
        imdb=show.imdb,
        status=status,
        current_episode_id=current_episode.id if current_episode else None,
        added_at=now,
        updated_at=now,
    )
    entry.show = show
    entry.current_episode = current_episode
    db.add(entry)
    db.flush()
    return entry
