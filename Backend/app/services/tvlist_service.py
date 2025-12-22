"""
TV list data access layer.
"""

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.utils.helpers import Helpers
from app.db.models import (
    DBTVShow as TVShowModel,
    DBTVList,
    DBProgress,
    DBEpisodeList,
    DBEpisode,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===============================================
# ============== GET TV LIST ====================
# ===============================================


def get_user_tv_list(user_id: str):
    """
    Get the user's TV list.

    :param user_id: The user ID.
    :return: Sorted list of TV shows.
    """
    print(f"User ID from JWT: {user_id}")

    with SessionLocal() as session:
        tvlist = session.query(TVList).filter(TVList.userId == user_id).first()
        if not tvlist:
            print("No tvlist found for user")
            return []

        tvshows = (
            session.query(TVShowModel)
            .filter(TVShowModel.tvListId == tvlist.tvListId)
            .all()
        )

        data = []
        for tv in tvshows:
            progress = (
                session.query(Progress)
                .filter(Progress.progressId == tv.progressId)
                .first()
            )
            episodes = []
            if tv.episodeListId:
                eps = (
                    session.query(Episode)
                    .filter(Episode.episodeListId == tv.episodeListId)
                    .all()
                )
                episodes = [{"code": e.code, "name": e.name} for e in eps]
            item = {
                "status": progress.status if progress else "unknown",
                "image": tv.image,
                "title": tv.title,
                "imdb": tv.imdb,
                "score": tv.score,
                "currentEpisodeIndex": progress.currentEpisodeIndex if progress else 0,
                "episodes": episodes,
            }
            data.append(item)

        sorted_data = sorted(data, key=lambda x: x.get("title", "").lower())
        return sorted_data


def get_user_tv_list_by_status(user_id: str, status: str):
    """
    Get the user's TV list filtered by status.

    :param user_id: The user ID.
    :param status: The status to filter by.
    :return: Filtered and sorted list of TV shows.
    """
    print(f"User ID from JWT: {user_id}")

    with SessionLocal() as session:
        tvlist = session.query(TVList).filter(TVList.userId == user_id).first()
        if not tvlist:
            print("No tvlist found for user")
            return []

        tvshows = (
            session.query(TVShowModel)
            .join(Progress, TVShowModel.progressId == Progress.progressId)
            .filter(TVShowModel.tvListId == tvlist.tvListId, Progress.status == status)
            .all()
        )

        data = []
        for tv in tvshows:
            progress = (
                session.query(Progress)
                .filter(Progress.progressId == tv.progressId)
                .first()
            )
            episodes = []
            if tv.episodeListId:
                eps = (
                    session.query(Episode)
                    .filter(Episode.episodeListId == tv.episodeListId)
                    .all()
                )
                episodes = [{"code": e.code, "name": e.name} for e in eps]
            item = {
                "status": progress.status if progress else "unknown",
                "image": tv.image,
                "title": tv.title,
                "imdb": tv.imdb,
                "score": tv.score,
                "currentEpisodeIndex": progress.currentEpisodeIndex if progress else 0,
                "episodes": episodes,
            }
            data.append(item)

        sorted_data = sorted(data, key=lambda x: x.get("title", "").lower())
        return sorted_data


# ===============================================
# ============== ADD / REMOVE SHOWS =============
# ===============================================


def add_tv_show(user_id: str, tv_show):
    """
    Add a TV show to the user's list.

    :param user_id: The user ID.
    :param tv_show: The TV show data.
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    with SessionLocal() as session:
        # Create Progress
        progress = Progress(
            status=tv_show.status, currentEpisodeIndex=tv_show.currentEpisodeIndex
        )
        session.add(progress)
        session.flush()

        # Create EpisodeList
        episode_list = EpisodeList()
        session.add(episode_list)
        session.flush()

        # Add Episodes
        for ep in tv_show.episodes:
            episode = Episode(
                episodeId=f"{tv_show.imdb}_{ep.code}",
                episodeListId=episode_list.episodeListId,
                name=ep.name,
                code=ep.code,
            )
            session.add(episode)

        # Add TVShow
        tv = TVShowModel(
            imdb=tv_show.imdb,
            tvListId=tvlist_id,
            title=tv_show.title,
            image=tv_show.image,
            score=tv_show.score,
            episodeListId=episode_list.episodeListId,
            progressId=progress.progressId,
        )
        session.add(tv)

        session.commit()

    print(f"[added tv show] user_id: {user_id}, title: {tv_show.title}")


def delete_tv_show(user_id: str, imdb: str):
    """
    Delete a TV show from the user's list by IMDb ID.

    :param user_id: The user ID.
    :param imdb: The IMDb ID.
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    with SessionLocal() as session:
        tvshow = (
            session.query(TVShowModel)
            .filter(TVShowModel.imdb == imdb, TVShowModel.tvListId == tvlist_id)
            .first()
        )
        if tvshow:
            # Delete related
            session.query(Episode).filter(
                Episode.episodeListId == tvshow.episodeListId
            ).delete()
            session.query(EpisodeList).filter(
                EpisodeList.episodeListId == tvshow.episodeListId
            ).delete()
            session.query(Progress).filter(
                Progress.progressId == tvshow.progressId
            ).delete()
            session.delete(tvshow)
            session.commit()

    print(f"[deleted show] user_id: {user_id}, imdb: {imdb}")


# ===============================================
# ============= UPDATE TV SHOW STATUS ===========
# ===============================================


def update_tv_show_status(user_id: str, imdb: str, new_status: str):
    """
    Update the status of a TV show in the user's list.

    :param user_id: The user ID.
    :param imdb: The IMDb ID.
    :param new_status: The new status.
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    with SessionLocal() as session:
        tvshow = (
            session.query(TVShowModel)
            .filter(TVShowModel.imdb == imdb, TVShowModel.tvListId == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(Progress)
                .filter(Progress.progressId == tvshow.progressId)
                .first()
            )
            if progress:
                progress.status = new_status
                session.commit()

    print(
        f"[updated status] user_id: {user_id}, imdb: {imdb}, new_status: {new_status}"
    )


# ===============================================
# =========== INCREMENT / DECREMENT =============
# ============= TV SHOW PROGRESS ================
# ===============================================


def decrement_tv_show_progress(user_id: str, imdb: str):
    """
    Decrement the progress of a TV show by one episode.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the TV show.
    :return: None
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    with SessionLocal() as session:
        tvshow = (
            session.query(TVShowModel)
            .filter(TVShowModel.imdb == imdb, TVShowModel.tvListId == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(Progress)
                .filter(Progress.progressId == tvshow.progressId)
                .first()
            )
            if progress and progress.currentEpisodeIndex > 0:
                progress.currentEpisodeIndex -= 1
                session.commit()
                print(f"[decremented progress] imdb: {imdb}")
            else:
                print(f"[decremented progress] imdb: {imdb} already at 0")
        else:
            print(f"[decremented progress] imdb: {imdb} not found")


def increment_tv_show_progress(user_id: str, imdb: str):
    """
    Increment the progress of a TV show by one episode.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the TV show.
    :return: None
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    with SessionLocal() as session:
        tvshow = (
            session.query(TVShowModel)
            .filter(TVShowModel.imdb == imdb, TVShowModel.tvListId == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(Progress)
                .filter(Progress.progressId == tvshow.progressId)
                .first()
            )
            episodes_count = (
                session.query(Episode)
                .filter(Episode.episodeListId == tvshow.episodeListId)
                .count()
            )
            if progress and progress.currentEpisodeIndex < episodes_count - 1:
                progress.currentEpisodeIndex += 1
                session.commit()
                print(f"[incremented progress] imdb: {imdb}")
            else:
                print(
                    f"[incremented progress] imdb: {imdb} already at last episode ({episodes_count})"
                )
        else:
            print(f"[incremented progress] imdb: {imdb} not found")


def update_by_index_tv_show_progress(user_id: str, imdb: str, index: int):
    """
    Update the progress of a TV show to a specific episode index.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the TV show.
    :param index: The episode index to set.
    :return: None
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    with SessionLocal() as session:
        tvshow = (
            session.query(TVShowModel)
            .filter(TVShowModel.imdb == imdb, TVShowModel.tvListId == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(Progress)
                .filter(Progress.progressId == tvshow.progressId)
                .first()
            )
            if progress:
                progress.currentEpisodeIndex = index
                session.commit()
                print(f"[update by index progress] imdb: {imdb}, set to: {index}")
        else:
            print(f"[update by index progress] imdb: {imdb} not found")
