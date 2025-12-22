from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import Optional

from app.db.models import UpdateMovieStatusRequest, UpdateStatusRequest, AddMovieRequest
from app.utils.helpers import Helpers
from app.services.movielist_service import (
    add_movie,
    delete_movie,
    get_user_movie_list,
    update_movie_status,
)

movies_router = APIRouter()


@movies_router.get("/movielist")
async def get_user_movie_list_route(
    user_id: str = Depends(Helpers.get_current_user),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """
    Get the user's movie list, optionally filtered by status.

    :param user_id: The authenticated user ID (injected automatically).
    :param status_filter: Optional status to filter by.
    :return: User's movie watchlist.
    """
    try:
        data = get_user_movie_list(user_id, status_filter)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@movies_router.post("/movielist/add", status_code=status.HTTP_201_CREATED)
async def add_movie_route(
    req: AddMovieRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Add a movie to the user's list.

    :param req: The add movie request.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        await add_movie(user_id, req)
        return {"message": "Movie added successfully", "req": req}
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
    :return: Success message on deletion.
    """
    try:
        result = delete_movie(user_id, imdb)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@movies_router.patch("/movielist/edit")
async def update_movie_status_route(
    req: UpdateMovieStatusRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Update the status of a movie in the user's list.

    :param req: The update request.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        update_movie_status(user_id, req)
        return {
            "message": "Movie status updated successfully",
            "imdb": req.imdb,
            "status": req.status,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
