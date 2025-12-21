from dotenv import load_dotenv
import uvicorn
from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
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


@app.post(f"{BASE_URI}/user/add")
async def __add_user(user_data: User):
    print(user_data)
    add_user(user_data)
    return {"message": "Adding User", "user_data": user_data}


@app.delete(f"{BASE_URI}/user/delete")
async def __delete_user(data: User):
    print(data)
    delete_user(data)
    return {"message": "Delete User endpoint hit", "data": data}


# ===============================================
# ============== AUTH ===========================
# ===============================================


@app.post(f"{BASE_URI}/login")
async def __login(data: User, response: Response, request: Request):
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

    return {"message": "User logged in", "data": data}


@app.get(f"{BASE_URI}/auth")
def _auth(request: Request):
    return auth(request)


@app.post(f"{BASE_URI}/logout")
async def __logout(response: Response, session_token: str = Cookie(None)):
    return logout(response, session_token)


# ===============================================
# ============== SEARCH =========================
# ===============================================


@app.get(f"{BASE_URI}/search/tv_show")
async def __search_tv_show(query: str = Query(..., alias="q")):
    """
    Searches all the tv shows by query string.

    :param query: The search query string.
    :return: A JSON response containing the search results.
    """
    data = await search_tv_show(query)
    return {"results": data}


@app.get(f"{BASE_URI}/search/movie")
async def __search_movie(query: str = Query(..., alias="q")):
    """
    Searches all the movies by query string.

    :param query: The search query string.
    :return: A JSON response containing the search results.
    """
    data = await search_movie(query)
    return {"results": data}


@app.get(f"{BASE_URI}/singlesearch/tv_show")
async def __search_tv_show_by_tvmaze_id(tvmaze_id: str = Query(..., alias="id")):
    """
    Searches a TV show by its TVmaze ID.

    :param tvmaze_id: The TVmaze ID of the TV show.
    :return: A JSON response containing the TV show details.
    """
    data = await search_tv_show_by_tvmaze_id(tvmaze_id)
    return {"results": data}


@app.get(f"{BASE_URI}/singlesearch/movie")
async def __search_movie_by_imdb_id(imdb: str = Query(..., alias="id")):
    """
    Searches a movie by its IMDb ID.
    :param imdb: The IMDb ID of the movie.
    :return: A JSON response containing the movie details.
    """
    data = await search_movie_by_imdb_id(imdb)
    return {"results": data}


# ===============================================
# ============== TV SHOWS =======================
# ===============================================


@app.get(f"{BASE_URI}/tvlist")
async def __get_user_tv_list(request: Request):
    data = get_user_tv_list(request)
    return {"watchlist": data}


@app.get(f"{BASE_URI}/tvlist/status")
async def __get_user_tv_list_by_status(
    request: Request, status: str = Query(..., alias="status")
):
    data = get_user_tv_list_by_status(request, status)
    return {"watchlist": data}


@app.post(f"{BASE_URI}/tvlist/add")
async def __add_tv_show(request: Request, data: TVShow):
    add_tv_show(request, data)
    return {"message": "Add TV List Item added", "data": data}


@app.delete(f"{BASE_URI}/tvlist/delete")
async def __delete_tv_show(request: Request, data: DeleteRequest):
    delete_tv_show(request, data.imdb)
    return {"message": "Delete TV List Item deleted", "imdb": data.imdb}


@app.patch(f"{BASE_URI}/tvlist/edit")
async def __update_tv_show_status(request: Request, data: UpdateStatusRequest):
    update_tv_show_status(request, data.imdb, data.new_status)
    return {
        "message": "Status endpoint hit",
        "imdb": data.imdb,
        "new_status": data.new_status,
    }


# ===============================================
# ========== TVLIST PROGRESS ====================
# ===============================================


@app.patch(f"{BASE_URI}/tvlist/progress/increment")
async def __increment_tv_show_progress(request: Request, data: UpdateProgressRequest):
    increment_tv_show_progress(request, data.imdb)
    return {"message": "Progress incremented", "imdb": data.imdb}


@app.patch(f"{BASE_URI}/tvlist/progress/decrement")
async def __decrement_tv_show_progress(request: Request, data: UpdateProgressRequest):
    decrement_tv_show_progress(request, data.imdb)
    return {"message": "Progress decremented", "imdb": data.imdb}


@app.patch(f"{BASE_URI}/tvlist/progress/index")
async def __update_by_index_tv_show_progress(
    request: Request, data: UpdateProgressByIndexRequest
):
    update_by_index_tv_show_progress(request, data.imdb, data.index)
    return {
        "message": "Progress updated by index",
        "imdb": data.imdb,
        "index": data.index,
    }


# ===============================================
# ============== MOVIES =========================
# ===============================================


@app.post(f"{BASE_URI}/movielist")
async def __get_user_movie_list(request: Request):
    data = get_user_movie_list(request)
    return {"watchlist": data}


@app.post(f"{BASE_URI}/movielist/{{status}}")
async def __get_user_movie_list_by_status(request: Request, status: str = Path(...)):
    print(f"TV LIST ROUTE HIT with status: {status}")
    data = get_user_movie_list_by_status(request, status)
    return {"watchlist": data}


@app.post(f"{BASE_URI}/movielist/add")
async def __add_movie(request: Request, movie_data: Movie):
    print(movie_data)
    add_movie(request, movie_data)
    return {"message": "Movie Added", "movie_data": movie_data}


@app.delete(f"{BASE_URI}/movielist/delete")
async def __delete_movie(request: Request, data: DeleteRequest):
    delete_movie(request, data.imdb)
    return {"message": "Delete Movie endpoint hit", "imdb": data.imdb}


@app.patch(f"{BASE_URI}/movielist/edit")
async def __update_movie_status(request: Request, data: UpdateStatusRequest):
    update_movie_status(request, data.imdb, data.new_status)
    return {
        "message": "Status endpoint hit",
        "imdb": data.imdb,
        "new_status": data.new_status,
    }


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(PORT), reload=False)
