from dotenv import load_dotenv
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Path
import os

from modules.auth_dal import auth
from modules.helpers import Helpers
from modules.models import (
    Movie,
    TVShow,
    UpdateStatusRequest,
    UpdateProgressRequest,
    UpdateProgressByIndexRequest,
    User,
)
from modules.movielist_dal import (
    add_movie,
    delete_movie,
    get_user_movie_list,
    get_user_movie_list_by_status,
    update_movie_status,
)
from modules.search_dal import (
    search_movie,
    search_movie_by_imdb_id,
    search_tv_show,
    search_tv_show_by_tvmaze_id,
)
from modules.sessions_dal import authenticate_user
from modules.tvlist_dal import (
    add_tv_show,
    decrement_tv_show_progress,
    delete_tv_show,
    get_user_tv_list,
    get_user_tv_list_by_status,
    increment_tv_show_progress,
    update_by_index_tv_show_progress,
    update_tv_show_status,
)
from modules.user_dal import add_user, delete_user


app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
DEV_MODE = os.environ["DEV_MODE"] == "true"
PORT = os.environ["PORT"]
BASE_URI = "/api/v1"

# ===============================================
# ============== USERS ==========================
# ===============================================


@app.post(f"{BASE_URI}/user/add", status_code=status.HTTP_201_CREATED)
async def add_user_route(user_data: User):
    """
    Add a new user to the system.

    :param user_data: The user data to add.
    :return: A JSON response with the added user data.
    """
    try:
        add_user(user_data)
        return {"message": "User added successfully", "user_data": user_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete(f"{BASE_URI}/user/delete")
async def delete_user_route(data: User):
    """
    Delete a user from the system.

    :param data: The user data to delete.
    :return: No content on success.
    """
    try:
        delete_user(data)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===============================================
# ============== AUTH ===========================
# ===============================================


@app.post(f"{BASE_URI}/login")
async def login_route(data: User, response: Response):
    """
    Log in a user and set JWT cookie.

    :param data: The user login data.
    :param response: The response object to set cookie.
    :return: A JSON response with login message.
    """
    try:
        user_id = authenticate_user(data)
        jwt_token = Helpers.create_jwt_token(user_id)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=True if DEV_MODE != "true" else False,
            samesite="lax",
            max_age=60 * 60 * 24,
        )
        return {"message": "User logged in successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get(f"{BASE_URI}/auth")
def auth_route(user_id: str = Depends(Helpers.get_current_user)):
    """
    Get authentication status for the current user.

    :param user_id: The authenticated user ID (injected automatically).
    :return: Authentication data.
    """
    try:
        return auth(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post(f"{BASE_URI}/logout")
async def logout_route(response: Response):
    """
    Log out the current user by clearing the JWT cookie.

    :param response: The response object to clear cookie.
    :return: Logout message.
    """
    try:
        response.delete_cookie("access_token")
        return {"message": "User logged out"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ===============================================
# ============== SEARCH =========================
# ===============================================


@app.get(f"{BASE_URI}/search/tv_show")
async def search_tv_show_route(query: str = Query(..., alias="q")):
    """
    Search for TV shows by query string.

    :param query: The search query.
    :return: Search results.
    """
    try:
        data = await search_tv_show(query)
        return {"results": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get(f"{BASE_URI}/search/movie")
async def search_movie_route(query: str = Query(..., alias="q")):
    """
    Search for movies by query string.

    :param query: The search query.
    :return: Search results.
    """
    try:
        data = await search_movie(query)
        return {"results": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get(f"{BASE_URI}/singlesearch/tv_show")
async def search_tv_show_by_tvmaze_id_route(tvmaze_id: str = Query(..., alias="id")):
    """
    Search for a TV show by TVmaze ID.

    :param tvmaze_id: The TVmaze ID.
    :return: TV show details.
    """
    try:
        data = await search_tv_show_by_tvmaze_id(tvmaze_id)
        return {"results": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get(f"{BASE_URI}/singlesearch/movie")
async def search_movie_by_imdb_id_route(imdb: str = Query(..., alias="id")):
    """
    Search for a movie by IMDb ID.

    :param imdb: The IMDb ID.
    :return: Movie details.
    """
    try:
        data = await search_movie_by_imdb_id(imdb)
        return {"results": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===============================================
# ============== TV SHOWS =======================
# ===============================================


@app.get(f"{BASE_URI}/tvlist")
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


@app.get(f"{BASE_URI}/tvlist/status")
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


@app.post(f"{BASE_URI}/tvlist/add", status_code=status.HTTP_201_CREATED)
async def add_tv_show_route(
    data: TVShow, user_id: str = Depends(Helpers.get_current_user)
):
    """
    Add a TV show to the user's list.

    :param data: The TV show data.
    :param user_id: The authenticated user ID (injected automatically).
    :return: Success message.
    """
    try:
        add_tv_show(user_id, data)
        return {"message": "TV show added successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete(f"{BASE_URI}/tvlist/{{imdb}}")
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


@app.patch(f"{BASE_URI}/tvlist/edit")
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


# ===============================================
# ========== TVLIST PROGRESS ====================
# ===============================================


@app.patch(f"{BASE_URI}/tvlist/progress/increment")
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


@app.patch(f"{BASE_URI}/tvlist/progress/decrement")
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


@app.patch(f"{BASE_URI}/tvlist/progress/index")
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


# ===============================================
# ============== MOVIES =========================
# ===============================================


@app.get(f"{BASE_URI}/movielist")
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


@app.get(f"{BASE_URI}/movielist/{{status_filter}}")
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


@app.post(f"{BASE_URI}/movielist/add", status_code=status.HTTP_201_CREATED)
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


@app.delete(f"{BASE_URI}/movielist/{{imdb}}")
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


@app.patch(f"{BASE_URI}/movielist/edit")
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


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(PORT), reload=False)
