"""
Movie list data access layer.
"""

from fastapi import HTTPException
import httpx
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import uuid
from typing import Optional
from app.core.database import engine
from app.utils.helpers import Helpers
from app.db.models import DBMovie, DBMovieList, DBProgress, AddMovieRequest, MovieData
from app.core.config import settings

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===============================================
# ============== GET MOVIE LIST =================
# ===============================================


def get_user_movie_list(user_id: str, status: Optional[str] = None):
    """
    Get the user's movie list, optionally filtered by status.

    :param user_id: The user ID.
    :param status: Optional status to filter by.
    :return: List of movies.
    """
    print(f"User ID: {user_id}")

    with SessionLocal() as session:
        movielist = (
            session.query(DBMovieList).filter(DBMovieList.user_id == user_id).first()
        )
        if not movielist:
            print("No movielist found for user")
            return []

        # Raw SQL to get movies with status
        sql = text(
            """
            SELECT m.imdb, m.title, m.image, m.score, p.status
            FROM movie m
            JOIN progress p ON m.progress_id = p.progress_id
            WHERE m.movie_list_id = :movie_list_id
            AND m.title IS NOT NULL
            AND m.image IS NOT NULL
            AND m.score IS NOT NULL
            AND (:status IS NULL OR p.status = :status)
            ORDER BY m.title ASC
            """
        )

        result = (
            session.execute(
                sql, {"movie_list_id": str(movielist.movie_list_id), "status": status}
            )
            .mappings()
            .all()
        )

        return result


# ===============================================
# ============== ADD / REMOVE MOVIES ============
# ===============================================


async def add_movie(user_id: str, req: AddMovieRequest):
    """
    Add a movie to the user's movie list.

    :param user_id: The user ID.
    :param req: The add movie request.
    """
    with SessionLocal() as session:
        # Get the user's movie list ID
        movielist = (
            session.query(DBMovieList).filter(DBMovieList.user_id == user_id).first()
        )
        if not movielist:
            raise HTTPException(status_code=404, detail="Movie list not found")
        movielist_id = str(movielist.movie_list_id)

        # Fetch movie details from OMDB
        _md: MovieData = await get_movie_data_by_imdb(req.imdb)

        # Create Progress
        progress = DBProgress(
            progress_id=str(uuid.uuid4()),
            status=req.status,
            current_episode_index=0,  # Movies don't have episodes
        )
        session.add(progress)
        session.flush()

        # Add Movie
        m = DBMovie(
            imdb=_md.imdb,
            movie_list_id=movielist_id,
            title=_md.title,
            image=_md.image,
            score=_md.score,
            progress_id=progress.progress_id,
        )
        session.add(m)
        session.commit()


def delete_movie(user_id: str, imdb: str):
    """
    Delete a movie from the user's movie list.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the movie.
    """
    with SessionLocal() as session:
        # Get the user's movie list ID
        movielist = (
            session.query(DBMovieList).filter(DBMovieList.user_id == user_id).first()
        )
        if not movielist:
            raise HTTPException(status_code=404, detail="Movie list not found")
        movielist_id = str(movielist.movie_list_id)

        movie = (
            session.query(DBMovie)
            .filter(DBMovie.imdb == imdb, DBMovie.movie_list_id == movielist_id)
            .first()
        )
        if movie:
            # Delete movie first to remove foreign key references
            session.delete(movie)
            session.flush()  # Execute the deletion to remove references
            # Then delete related progress
            session.query(DBProgress).filter(
                DBProgress.progress_id == movie.progress_id
            ).delete()
            session.commit()
            return {"message": "Movie deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Movie not found")


# ===============================================
# ============ UPDATE MOVIE STATUS ==============
# ===============================================


def update_movie_status(user_id: str, imdb: str, status: str):
    """
    Update the status of a movie in the user's movie list.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the movie.
    :param status: The new status.
    """
    with SessionLocal() as session:
        # Get the user's movie list ID
        movielist = (
            session.query(DBMovieList).filter(DBMovieList.user_id == user_id).first()
        )
        if not movielist:
            raise HTTPException(status_code=404, detail="Movie list not found")
        movielist_id = str(movielist.movie_list_id)

        movie = (
            session.query(DBMovie)
            .filter(DBMovie.imdb == imdb, DBMovie.movie_list_id == movielist_id)
            .first()
        )
        if movie:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progress_id == movie.progress_id)
                .first()
            )
            if progress:
                progress.status = status
                session.commit()


# ===============================================
# =========== FETCH FULL DATA HELPERS ===========
# ===============================================
async def get_movie_data_by_imdb(imdb_id: str) -> MovieData:
    """
    Get movie details by IMDB ID using OMDB API.

    :param imdb_id: The IMDB ID.
    :return: MovieData object.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://www.omdbapi.com/?apikey={settings.omdb_api_key}&i={imdb_id}"
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
            if data.get("Response") == "True":
                return MovieData(
                    title=data.get("Title"),
                    image=data.get("Poster"),
                    imdb=data.get("imdbID"),
                    score=(
                        float(data.get("imdbRating"))
                        if data.get("imdbRating") != "N/A"
                        else 0.0
                    ),
                )
            else:
                raise HTTPException(status_code=404, detail="Movie not found")
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail=f"OMDB error: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching movie: {str(e)}"
            )
