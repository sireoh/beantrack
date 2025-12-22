"""
Movie list data access layer.
"""

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.utils.helpers import Helpers
from app.db.models import DBMovie, DBMovieList, DBProgress

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===============================================
# ============== GET MOVIE LIST =================
# ===============================================


def get_user_movie_list(user_id: str):
    """
    Get the user's movie list.

    :param user_id: The user ID.
    :return: List of movies.
    """
    print(f"User ID: {user_id}")

    with SessionLocal() as session:
        movielist = (
            session.query(DBMovieList).filter(DBMovieList.userid == user_id).first()
        )
        if not movielist:
            print("No movielist found for user")
            return []

        movies = (
            session.query(DBMovie)
            .filter(DBMovie.movielistid == movielist.movielistid)
            .all()
        )

        data = []
        for movie in movies:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progressid == movie.progressid)
                .first()
            )
            item = {
                "status": progress.status if progress else "unknown",
                "image": movie.image,
                "title": movie.title,
                "imdb": movie.imdb,
                "score": movie.score,
            }
            data.append(item)

        return data


def get_user_movie_list_by_status(user_id: str, status: str):
    """
    Get the user's movie list filtered by status.

    :param user_id: The user ID.
    :param status: The status to filter by.
    :return: Filtered list of movies.
    """
    print(f"User ID: {user_id}")

    with SessionLocal() as session:
        movielist = (
            session.query(DBMovieList).filter(DBMovieList.userid == user_id).first()
        )
        if not movielist:
            print("No movielist found for user")
            return []

        movies = (
            session.query(DBMovie)
            .join(DBProgress, DBMovie.progressid == DBProgress.progressid)
            .filter(
                DBMovie.movielistid == movielist.movielistid,
                DBProgress.status == status,
            )
            .all()
        )

        data = []
        for movie in movies:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progressId == movie.progressId)
                .first()
            )
            item = {
                "status": progress.status if progress else "unknown",
                "image": movie.image,
                "title": movie.title,
                "imdb": movie.imdb,
                "score": movie.score,
            }
            data.append(item)

        return data


# ===============================================
# ============== ADD / REMOVE MOVIES ============
# ===============================================


def add_movie(user_id: str, movie):
    """
    Add a movie to the user's movie list.

    :param user_id: The user ID.
    :param movie: The movie to add.
    :return: None
    """
    movielist_id = Helpers.get_current_movielist_id(user_id)

    with SessionLocal() as session:
        # Create Progress
        progress = DBProgress(
            status=movie.status, currentEpisodeIndex=0
        )  # Movies don't have episodes, so 0
        session.add(progress)
        session.flush()

        # Add Movie
        m = DBMovie(
            imdb=movie.imdb,
            movielistid=movielist_id,
            title=movie.title,
            image=movie.image,
            score=movie.score,
            progressid=progress.progressid,
        )
        session.add(m)

        session.commit()

    print(f"[added movie] user_id: {user_id}, title: {movie.title}")


def delete_movie(user_id: str, imdb: str):
    """
    Delete a movie from the user's movie list.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the movie.
    :return: None
    """
    movielist_id = Helpers.get_current_movielist_id(user_id)

    with SessionLocal() as session:
        movie = (
            session.query(DBMovie)
            .filter(DBMovie.imdb == imdb, DBMovie.movielistid == movielist_id)
            .first()
        )
        if movie:
            session.query(DBProgress).filter(
                DBProgress.progressid == movie.progressid
            ).delete()
            session.delete(movie)
            session.commit()

    print(f"[deleted movie] user_id: {user_id}, imdb: {imdb}")


# ===============================================
# ============ UPDATE MOVIE STATUS ==============
# ===============================================


def update_movie_status(user_id: str, imdb: str, new_status: str):
    """
    Update the status of a movie in the user's movie list.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the movie.
    :param new_status: The new status.
    :return: None
    """
    movielist_id = Helpers.get_current_movielist_id(user_id)

    with SessionLocal() as session:
        movie = (
            session.query(DBMovie)
            .filter(DBMovie.imdb == imdb, DBMovie.movielistid == movielist_id)
            .first()
        )
        if movie:
            progress = (
                session.query(DBProgress)
                .filter(DBProgress.progressid == movie.progressid)
                .first()
            )
            if progress:
                progress.status = new_status  # type: ignore
                session.commit()

    print(
        f"[updated status] user_id: {user_id}, imdb: {imdb}, new_status: {new_status}"
    )
