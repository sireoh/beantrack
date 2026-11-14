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
            selectinload(TvList.entries)
            .selectinload(UserTvShow.show)
            .selectinload(TvShow.episodes),
        )
    )
    return db.scalars(stmt).one_or_none()


def get_entry(db: Session, tvlist_id: str, imdb: str) -> UserTvShow | None:
    return db.get(UserTvShow, (tvlist_id, imdb))


def delete_entry(db: Session, entry: UserTvShow) -> None:
    db.delete(entry)


def add_entry(
    db: Session,
    *,
    tvlist: TvList,
    show: TvShow,
    status: WatchStatus,
    current_episode: int,
    now: datetime,
) -> UserTvShow:
    entry = UserTvShow(
        tvlist_id=tvlist.tvlist_id,
        imdb=show.imdb,
        status=status,
        current_episode=current_episode,
        added_at=now,
        updated_at=now,
    )
    entry.show = show
    db.add(entry)
    db.flush()
    return entry


def update_progress(
    db: Session,
    entry: UserTvShow,
    *,
    current_episode: int,
    current_episode_metadata: dict[str, object],
) -> UserTvShow:
    entry.current_episode = current_episode
    entry.current_episode_metadata = current_episode_metadata
    db.commit()
    return entry
