"""
TV list data access layer.
"""

from fastapi import HTTPException
import httpx
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import uuid
from typing import Optional
from app.core.database import engine
from app.db.models import (
    AddTVShowRequest,
    DBTVShow,
    DBTVList,
    DBProgress,
    DBEpisode,
    DBEpisodeList,
    TVShowData,
    EpisodeData,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===============================================
# ============== GET TV LIST ====================
# ===============================================


def get_user_tv_list(user_id: str, status: Optional[str] = None):
    """
    Get the user's TV list, optionally filtered by status.

    :param user_id: The user ID.
    :param status: Optional status to filter by.
    :return: Sorted list of TV shows.
    """
    print(f"User ID from JWT: {user_id}")

    with SessionLocal() as session:
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            print("No tvlist found for user")
            return []

        # Raw SQL to flatten data with JSON aggregation
        sql = text(
            """
            SELECT tv.imdb, tv.title, tv.image, tv.score, p.status, p.current_episode_index AS "currentEpisodeIndex",
                   COALESCE(json_agg(
                       json_build_object('name', ep.name, 'code', CONCAT('S', LPAD(ep.season::text, 2, '0'), 'E', LPAD(ep.number::text, 2, '0')))
                   ) FILTER (WHERE ep.episode_id IS NOT NULL), '[]'::json) AS episodes
            FROM tvshow tv
            JOIN progress p ON tv.progress_id = p.progress_id
            LEFT JOIN episode ep ON tv.episode_list_id = ep.episode_list_id
            WHERE tv.tv_list_id = :tv_list_id
            AND tv.title IS NOT NULL
            AND tv.image IS NOT NULL
            AND tv.score IS NOT NULL
            AND (:status IS NULL OR p.status = :status)
            GROUP BY tv.imdb, tv.title, tv.image, tv.score, p.status, p.current_episode_index
            ORDER BY tv.title ASC
        """
        )

        result = (
            session.execute(
                sql, {"tv_list_id": str(tvlist.tv_list_id), "status": status}
            )
            .mappings()
            .all()
        )

        return result


def get_user_tv_list_by_status(user_id: str, status: str):
    """
    Get the user's TV list filtered by status.

    :param user_id: The user ID.
    :param status: The status to filter by.
    :return: Filtered and sorted list of TV shows.
    """
    print(f"User ID from JWT: {user_id}")

    with SessionLocal() as session:
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            print("No tvlist found for user")
            return []

        tvshows = (
            session.query(DBTVShow)
            .join(DBProgress, DBTVShow.progress_id == DBProgress.progress_id)
            .filter(
                DBTVShow.tv_list_id == tvlist.tv_list_id, DBProgress.status == status
            )
            .all()
        )

        data = []
        for tv in tvshows:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progress_id == tv.progress_id)
                .first()
            )
            episodes = []
            if tv.episode_list_id:
                eps = (
                    session.query(DBEpisode)
                    .filter(DBEpisode.episode_list_id == tv.episode_list_id)
                    .all()
                )
                episodes = [
                    {"code": f"S{e.season:02d}E{e.number:02d}", "name": e.name}
                    for e in eps
                ]
            item = {
                "status": progress.status if progress else "unknown",
                "image": tv.image,
                "title": tv.title,
                "imdb": tv.imdb,
                "score": tv.score,
                "currentEpisodeIndex": (
                    progress.current_episode_index if progress else 0
                ),
                "episodes": episodes,
            }
            data.append(item)


# ===============================================
# ============== ADD / REMOVE SHOWS =============
# ===============================================


async def add_tv_show(user_id: str, req: AddTVShowRequest):
    """
    Add a TV show to the user's list.

    :param user_id: The user ID.
    :param tvmaze_id: The TVMaze ID.
    """
    with SessionLocal() as session:
        # Get the user's TV list ID
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            raise HTTPException(status_code=404, detail="TV list not found")
        tvlist_id = str(tvlist.tv_list_id)

        # Fetch show details from TVMaze
        _tsd: TVShowData = await get_tv_show_data(req.tvmaze_id)

        # Create DBProgress
        progress = DBProgress(
            progress_id=str(uuid.uuid4()),
            status=req.status,
            current_episode_index=0,
        )
        session.add(progress)
        session.flush()

        # Create DBEpisodeList
        episode_list = DBEpisodeList(episode_list_id=str(uuid.uuid4()))
        session.add(episode_list)
        session.flush()

        # Add Episodes
        episodes = [
            DBEpisode(
                episode_id=ep.episode_id,
                episode_list_id=episode_list.episode_list_id,
                name=ep.name,
                season=ep.season,
                number=ep.number,
            )
            for ep in _tsd.episodes
        ]
        session.add_all(episodes)

        # Add TVShow
        tv = DBTVShow(
            imdb=_tsd.imdb,
            tv_list_id=tvlist_id,
            title=_tsd.title,
            image=_tsd.image,
            score=_tsd.score,
            episode_list_id=episode_list.episode_list_id,
            progress_id=progress.progress_id,
        )
        session.add(tv)
        session.commit()


def delete_tv_show(user_id: str, id: str):
    """
    Delete a TV show from the user's list by ID.

    :param user_id: The user ID.
    :param id: The ID.
    """
    with SessionLocal() as session:
        # Get the user's TV list ID
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            raise HTTPException(status_code=404, detail="TV list not found")
        tvlist_id = str(tvlist.tv_list_id)

        tvshow = (
            session.query(DBTVShow)
            .filter(DBTVShow.imdb == id, DBTVShow.tv_list_id == tvlist_id)
            .first()
        )
        if tvshow:
            # Delete TV show first to remove foreign key references
            session.delete(tvshow)
            session.flush()  # Execute the deletion to remove references
            # Then delete related records in dependency order
            session.query(DBEpisode).filter(
                DBEpisode.episode_list_id == tvshow.episode_list_id
            ).delete()
            session.query(DBEpisodeList).filter(
                DBEpisodeList.episode_list_id == tvshow.episode_list_id
            ).delete()
            session.query(DBProgress).filter(
                DBProgress.progress_id == tvshow.progress_id
            ).delete()
            session.commit()
            return {"message": "TV show deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="TV show not found")


# ===============================================
# ============= UPDATE TV SHOW STATUS ===========
# ===============================================


def update_tv_show_status(user_id: str, imdb: str, status: str):
    """
    Update the status of a TV show in the user's list.

    :param user_id: The user ID.
    :param imdb: The IMDb ID.
    :param status: The new status.
    """
    with SessionLocal() as session:
        # Get the user's TV list ID
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            raise HTTPException(status_code=404, detail="TV list not found")
        tvlist_id = str(tvlist.tv_list_id)

        tvshow = (
            session.query(DBTVShow)
            .filter(DBTVShow.imdb == imdb, DBTVShow.tv_list_id == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progress_id == tvshow.progress_id)
                .first()
            )
            if progress:
                progress.status = status
                session.commit()


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
    with SessionLocal() as session:
        # Get the user's TV list ID
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            raise HTTPException(status_code=404, detail="TV list not found")
        tvlist_id = str(tvlist.tv_list_id)

        tvshow = (
            session.query(DBTVShow)
            .filter(DBTVShow.imdb == imdb, DBTVShow.tv_list_id == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progress_id == tvshow.progress_id)
                .first()
            )
            if progress and progress.current_episode_index > 0:
                progress.current_episode_index -= 1
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
    with SessionLocal() as session:
        # Get the user's TV list ID
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            raise HTTPException(status_code=404, detail="TV list not found")
        tvlist_id = str(tvlist.tv_list_id)

        tvshow = (
            session.query(DBTVShow)
            .filter(DBTVShow.imdb == imdb, DBTVShow.tv_list_id == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progress_id == tvshow.progress_id)
                .first()
            )
            episodes_count = (
                session.query(DBEpisode)
                .filter(DBEpisode.episode_list_id == tvshow.episode_list_id)
                .count()
            )
            if progress and progress.current_episode_index < episodes_count - 1:
                progress.current_episode_index += 1
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
    with SessionLocal() as session:
        # Get the user's TV list ID
        tvlist = session.query(DBTVList).filter(DBTVList.user_id == user_id).first()
        if not tvlist:
            raise HTTPException(status_code=404, detail="TV list not found")
        tvlist_id = str(tvlist.tv_list_id)

        tvshow = (
            session.query(DBTVShow)
            .filter(DBTVShow.imdb == imdb, DBTVShow.tv_list_id == tvlist_id)
            .first()
        )
        if tvshow:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progress_id == tvshow.progress_id)
                .first()
            )
            if progress:
                progress.current_episode_index = index
                session.commit()
                print(f"[update by index progress] imdb: {imdb}, set to: {index}")
        else:
            print(f"[update by index progress] imdb: {imdb} not found")


# ===============================================
# =========== FETCH FULL DATA HELPERS ===========
# ===============================================
async def get_tv_show_data(tvmaze_id: int) -> TVShowData:
    """
    Get full show details AND all episodes in a single API call.

    :param tvmaze_id: The TVMaze ID (e.g., "139")
    :return: TVShowData object containing show metadata and episodes.
    """
    async with httpx.AsyncClient() as client:
        try:
            # We call the main show endpoint and tell TVMaze to "embed" the episodes
            url = f"https://api.tvmaze.com/shows/{tvmaze_id}?embed=episodes"
            res = await client.get(url)
            res.raise_for_status()  # Check for 404s or 500s

            data = res.json()

            # Extract episodes from the special '_embedded' key
            raw_episodes = data.get("_embedded", {}).get("episodes", [])

            episodes = [
                EpisodeData(
                    episode_id=f"{data.get('name')}_{ep.get('season')}_{ep.get('number')}",
                    name=ep.get("name"),
                    season=ep.get("season"),
                    number=ep.get("number"),
                )
                for ep in raw_episodes
            ]

            # Return a TVShowData object
            return TVShowData(
                title=data.get("name"),
                image=data.get("image", {}).get("original"),
                imdb=data.get("externals", {}).get("imdb"),
                score=data.get("rating", {}).get("average"),
                episodes=episodes,
            )

        except httpx.HTTPStatusError as e:
            # For errors, return a minimal object or raise
            raise HTTPException(
                status_code=e.response.status_code, detail=f"TVMaze error: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching TV show: {str(e)}"
            )
