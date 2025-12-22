from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.db.models import Movie, UpdateStatusRequest
from app.utils.helpers import Helpers
from app.services.movielist_service import (
    add_movie,
    delete_movie,
    get_user_movie_list,
    get_user_movie_list_by_status,
    update_movie_status,
)

movies_router = APIRouter()


@movies_router.get("/movielist")
async def get_user_movie_list_route(user_id: str = Depends(Helpers.get_current_user)):
    """
    Get the user's movie list.

    :param user_id: The authenticated user ID (injected automatically).
    :return: User's movie watchlist.
    """
    try:
        data = get_user_movie_list(user_id)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@movies_router.get("/movielist/{status_filter}")
async def get_user_movie_list_by_status_route(
    user_id: str = Depends(Helpers.get_current_user), status_filter: str = Path(...)
):
    """
    Get the user's movie list filtered by status.

    :param user_id: The authenticated user ID (injected automatically).
    :param status_filter: The status to filter by.
    :return: Filtered movie watchlist.
    """
    try:
        data = get_user_movie_list_by_status(user_id, status_filter)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@movies_router.post("/movielist/add", status_code=status.HTTP_201_CREATED)
async def add_movie_route(
    movie_data: Movie, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Add a movie to the user's list.

    :param movie_data: The movie data.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        add_movie(user_id, movie_data)
        return {"message": "Movie added successfully", "movie_data": movie_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@movies_router.delete("/movielist/{imdb}")
async def delete_movie_route(
    user_id: str = Depends(Helpers.get_current_user), imdb: str = Path(...)
):
    """
    Delete a movie from the user's list.

    :param user_id: The authenticated user ID (injected automatically).
    :param imdb: The IMDB ID of the movie.
    :return: No content on success.
    """
    try:
        delete_movie(user_id, imdb)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@movies_router.patch("/movielist/edit")
async def update_movie_status_route(
    data: UpdateStatusRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Update the status of a movie in the user's list.

    :param data: The update request data.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        update_movie_status(user_id, data.imdb, data.new_status)
        return {
            "message": "Movie status updated successfully",
            "imdb": data.imdb,
            "new_status": data.new_status,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
