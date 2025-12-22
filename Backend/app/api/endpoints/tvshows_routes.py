from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.db.models import (
    AddTVShowRequest,
    UpdateProgressByIndexRequest,
    UpdateProgressRequest,
    UpdateStatusRequest,
)
from app.utils.helpers import Helpers
from app.services.tvlist_service import (
    add_tv_show,
    decrement_tv_show_progress,
    delete_tv_show,
    get_user_tv_list,
    get_user_tv_list_by_status,
    increment_tv_show_progress,
    update_by_index_tv_show_progress,
    update_tv_show_status,
)

tvshows_router = APIRouter()


@tvshows_router.get("/tvlist")
async def get_user_tv_list_route(user_id: str = Depends(Helpers.get_current_user)):
    """
    Get the user's TV list.

    :param user_id: The authenticated user ID (injected automatically).
    :return: User's TV watchlist.
    """
    try:
        data = get_user_tv_list(user_id)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@tvshows_router.get("/tvlist/status")
async def get_user_tv_list_by_status_route(
    user_id: str = Depends(Helpers.get_current_user),
    status_filter: str = Query(..., alias="status"),
):
    """
    Get the user's TV list filtered by status.

    :param user_id: The authenticated user ID (injected automatically).
    :param status_filter: The status to filter by.
    :return: Filtered TV watchlist.
    """
    try:
        data = get_user_tv_list_by_status(user_id, status_filter)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@tvshows_router.post("/tvlist/add", status_code=status.HTTP_201_CREATED)
async def add_tv_show_route(
    req: AddTVShowRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Add a TV show to the user's list.

    :param req: The TV show data.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        await add_tv_show(user_id, req)
        return {"message": "TV show added successfully", "req": req}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tvshows_router.delete("/tvlist/{imdb}")
async def delete_tv_show_route(
    user_id: str = Depends(Helpers.get_current_user), imdb: str = Path(...)
):
    """
    Delete a TV show from the user's list.

    :param user_id: The authenticated user ID (injected automatically).
    :param imdb: The IMDB ID of the TV show.
    :return: No content on success.
    """
    try:
        delete_tv_show(user_id, imdb)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tvshows_router.patch("/tvlist/edit")
async def update_tv_show_status_route(
    data: UpdateStatusRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Update the status of a TV show in the user's list.

    :param user_id: The authenticated user ID (injected automatically).
    :param data: The update request data.
    :return: Success message.
    """
    try:
        update_tv_show_status(user_id, data.imdb, data.new_status)
        return {
            "message": "TV show status updated successfully",
            "imdb": data.imdb,
            "new_status": data.new_status,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tvshows_router.patch("/tvlist/progress/increment")
async def increment_tv_show_progress_route(
    data: UpdateProgressRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Increment the progress of a TV show.

    :param user_id: The authenticated user ID (injected automatically).
    :param data: The progress update data.
    :return: Success message.
    """
    try:
        increment_tv_show_progress(user_id, data.imdb)
        return {"message": "Progress incremented successfully", "imdb": data.imdb}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tvshows_router.patch("/tvlist/progress/decrement")
async def decrement_tv_show_progress_route(
    data: UpdateProgressRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Decrement the progress of a TV show.

    :param user_id: The authenticated user ID (injected automatically).
    :param data: The progress update data.
    :return: Success message.
    """
    try:
        decrement_tv_show_progress(user_id, data.imdb)
        return {"message": "Progress decremented successfully", "imdb": data.imdb}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tvshows_router.patch("/tvlist/progress/index")
async def update_by_index_tv_show_progress_route(
    data: UpdateProgressByIndexRequest, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Update the progress of a TV show to a specific index.

    :param data: The progress update by index data.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        update_by_index_tv_show_progress(user_id, data.imdb, data.index)
        return {
            "message": "Progress updated by index successfully",
            "imdb": data.imdb,
            "index": data.index,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
