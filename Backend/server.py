from dotenv import load_dotenv
import uvicorn
from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Path
import os

from Backend.modules.auth_dal import auth
from Backend.modules.helpers import Helpers
from Backend.modules.models import (
    Movie,
    TVShow,
    UpdateStatusRequest,
    DeleteRequest,
    UpdateProgressRequest,
    UpdateProgressByIndexRequest,
    User,
)
from Backend.modules.movielist_dal import (
    add_movie,
    delete_movie,
    get_user_movie_list,
    get_user_movie_list_by_status,
    update_movie_status,
)
from Backend.modules.search_dal import (
    search_movie,
    search_movie_by_imdb_id,
    search_tv_show,
    search_tv_show_by_tvmaze_id,
)
from Backend.modules.sessions_dal import login, logout
from Backend.modules.tvlist_dal import (
    add_tv_show,
    decrement_tv_show_progress,
    delete_tv_show,
    get_user_tv_list,
    get_user_tv_list_by_status,
    increment_tv_show_progress,
    update_by_index_tv_show_progress,
    update_tv_show_status,
)
from Backend.modules.user_dal import add_user, delete_user


app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def __add_user(user_data: User):
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
async def __delete_user(data: User):
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
async def __login(data: User, response: Response, request: Request):
    """
    Log in a user and set session cookie.

    :param data: The user login data.
    :param response: The response object to set cookie.
    :param request: The request object.
    :return: A JSON response with login message.
    """
    try:
        _r = login(request, data)
        session_id = _r["session_id"]
        signed_session = Helpers.sign_session_id(session_id)
        response.set_cookie(
            key="session_token",
            value=signed_session,
            httponly=True,
            secure=True if not DEV_MODE else False,
            samesite="lax",
            max_age=60 * 60 * 24,
        )
        return {"message": "User logged in successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get(f"{BASE_URI}/auth")
def _auth(request: Request):
    """
    Get authentication status for the current user.

    :param request: The request object.
    :return: Authentication data.
    """
    try:
        return auth(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post(f"{BASE_URI}/logout")
async def __logout(response: Response, session_token: str = Cookie(None)):
    """
    Log out the current user by clearing the session.

    :param response: The response object to clear cookie.
    :param session_token: The session token from cookie.
    :return: Logout message.
    """
    try:
        return logout(response, session_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ===============================================
# ============== SEARCH =========================
# ===============================================


@app.get(f"{BASE_URI}/search/tv_show")
async def __search_tv_show(query: str = Query(..., alias="q")):
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
async def __search_movie(query: str = Query(..., alias="q")):
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
async def __search_tv_show_by_tvmaze_id(tvmaze_id: str = Query(..., alias="id")):
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
async def __search_movie_by_imdb_id(imdb: str = Query(..., alias="id")):
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
async def __get_user_tv_list(request: Request):
    """
    Get the user's TV list.

    :param request: The request object.
    :return: User's TV watchlist.
    """
    try:
        data = get_user_tv_list(request)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get(f"{BASE_URI}/tvlist/status")
async def __get_user_tv_list_by_status(
    request: Request, status_filter: str = Query(..., alias="status")
):
    """
    Get the user's TV list filtered by status.

    :param request: The request object.
    :param status_filter: The status to filter by.
    :return: Filtered TV watchlist.
    """
    try:
        data = get_user_tv_list_by_status(request, status_filter)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post(f"{BASE_URI}/tvlist/add", status_code=status.HTTP_201_CREATED)
async def __add_tv_show(request: Request, data: TVShow):
    """
    Add a TV show to the user's list.

    :param request: The request object.
    :param data: The TV show data.
    :return: Success message.
    """
    try:
        add_tv_show(request, data)
        return {"message": "TV show added successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete(f"{BASE_URI}/tvlist/delete")
async def __delete_tv_show(request: Request, data: DeleteRequest):
    """
    Delete a TV show from the user's list.

    :param request: The request object.
    :param data: The delete request data.
    :return: No content on success.
    """
    try:
        delete_tv_show(request, data.imdb)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.patch(f"{BASE_URI}/tvlist/edit")
async def __update_tv_show_status(request: Request, data: UpdateStatusRequest):
    """
    Update the status of a TV show in the user's list.

    :param request: The request object.
    :param data: The update request data.
    :return: Success message.
    """
    try:
        update_tv_show_status(request, data.imdb, data.new_status)
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
async def __increment_tv_show_progress(request: Request, data: UpdateProgressRequest):
    """
    Increment the progress of a TV show.

    :param request: The request object.
    :param data: The progress update data.
    :return: Success message.
    """
    try:
        increment_tv_show_progress(request, data.imdb)
        return {"message": "Progress incremented successfully", "imdb": data.imdb}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.patch(f"{BASE_URI}/tvlist/progress/decrement")
async def __decrement_tv_show_progress(request: Request, data: UpdateProgressRequest):
    """
    Decrement the progress of a TV show.

    :param request: The request object.
    :param data: The progress update data.
    :return: Success message.
    """
    try:
        decrement_tv_show_progress(request, data.imdb)
        return {"message": "Progress decremented successfully", "imdb": data.imdb}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.patch(f"{BASE_URI}/tvlist/progress/index")
async def __update_by_index_tv_show_progress(
    request: Request, data: UpdateProgressByIndexRequest
):
    """
    Update the progress of a TV show to a specific index.

    :param request: The request object.
    :param data: The progress update by index data.
    :return: Success message.
    """
    try:
        update_by_index_tv_show_progress(request, data.imdb, data.index)
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


@app.post(f"{BASE_URI}/movielist")
async def __get_user_movie_list(request: Request):
    """
    Get the user's movie list.

    :param request: The request object.
    :return: User's movie watchlist.
    """
    try:
        data = get_user_movie_list(request)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post(f"{BASE_URI}/movielist/{{status_filter}}")
async def __get_user_movie_list_by_status(request: Request, status_filter: str = Path(...)):
    """
    Get the user's movie list filtered by status.

    :param request: The request object.
    :param status_filter: The status to filter by.
    :return: Filtered movie watchlist.
    """
    try:
        data = get_user_movie_list_by_status(request, status_filter)
        return {"watchlist": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post(f"{BASE_URI}/movielist/add", status_code=status.HTTP_201_CREATED)
async def __add_movie(request: Request, movie_data: Movie):
    """
    Add a movie to the user's list.

    :param request: The request object.
    :param movie_data: The movie data.
    :return: Success message.
    """
    try:
        print(movie_data)
        add_movie(request, movie_data)
        return {"message": "Movie added successfully", "movie_data": movie_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete(f"{BASE_URI}/movielist/delete")
async def __delete_movie(request: Request, data: DeleteRequest):
    """
    Delete a movie from the user's list.

    :param request: The request object.
    :param data: The delete request data.
    :return: No content on success.
    """
    try:
        delete_movie(request, data.imdb)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.patch(f"{BASE_URI}/movielist/edit")
async def __update_movie_status(request: Request, data: UpdateStatusRequest):
    """
    Update the status of a movie in the user's list.

    :param request: The request object.
    :param data: The update request data.
    :return: Success message.
    """
    try:
        update_movie_status(request, data.imdb, data.new_status)
        return {
            "message": "Movie status updated successfully",
            "imdb": data.imdb,
            "new_status": data.new_status,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(PORT), reload=False)
