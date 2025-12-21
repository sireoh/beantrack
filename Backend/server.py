from dotenv import load_dotenv
import uvicorn
from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Path
import os

from Backend.modules.auth_dal import get_auth
from Backend.modules.helpers import Helpers
from Backend.modules.models import Movie, TVShow, User
from Backend.modules.movielist_dal import (
    add_movie,
    delete_movie,
    get_user_movie_list,
    get_user_movie_list_by_status,
    update_movie_status,
)
from Backend.modules.search_dal import (
    search_movie,
    search_movie_by_imdb,
    search_tv_show,
    search_tv_show_by_tvmaze_id,
)
from Backend.modules.sessions_dal import add_session, delete_session
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

# ===============================================
# ============== USERS ==========================
# ===============================================


@app.post("/api/add/user")
async def __add_user(data: User):
    print(data)
    add_user(data)
    return {"message": "Add User endpoint hit", "data": data}


@app.delete("/api/delete/user")
async def __delete_user(data: User):
    print(data)
    delete_user(data)
    return {"message": "Delete User endpoint hit", "data": data}


# ===============================================
# ============== SESSIONS =======================
# ===============================================


@app.post("/api/login")
async def __login(data: User, response: Response, request: Request):
    _r = add_session(request, data)

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


@app.post("/api/logout")
async def __logout(response: Response, session_token: str = Cookie(None)):
    return delete_session(response, session_token)


# ===============================================
# ============== SEARCH =========================
# ===============================================


@app.post("/api/search/tv_show")
async def __search_tv_show(query: str = Query(..., alias="q")):
    data = await search_tv_show(query)
    return {"results": data}


@app.post("/api/search/movie")
async def __search_movie(query: str = Query(..., alias="q")):
    data = await search_movie(query)
    return {"results": data}


@app.post("/api/search_by_tvmaze_id/tv_show")
async def __search_tv_show_by_tvmaze_id(tvmaze_id: str = Query(..., alias="id")):
    data = await search_tv_show_by_tvmaze_id(tvmaze_id)
    return {"results": data}


@app.post("/api/search_by_imdb/movie")
async def __search_movie_by_imdb(imdb: str = Query(..., alias="i")):
    data = await search_movie_by_imdb(imdb)
    return {"results": data}


# ===============================================
# ============== AUTH ===========================
# ===============================================


@app.get("/api/auth")
def __get_auth(request: Request):
    return get_auth(request)


# ===============================================
# ============== TV SHOWS =======================
# ===============================================


@app.post("/api/tvlist")
async def __get_user_tv_list(request: Request):
    data = get_user_tv_list(request)
    return {"watchlist": data}


@app.post("/api/tvlist/{status}")
async def __get_user_tv_list_by_status(request: Request, status: str = Path(...)):
    print(f"TV LIST ROUTE HIT with status: {status}")
    data = get_user_tv_list_by_status(request, status)
    return {"watchlist": data}


@app.post("/api/add/tv_show")
async def __add_tv_show(request: Request, data: TVShow):
    add_tv_show(request, data)
    return {"message": "Add TV Show endpoint hit", "data": data}


@app.delete("/api/delete/{imdb}/tv_show")
async def __delete_tv_show(request: Request, imdb: str = Path(...)):
    delete_tv_show(request, imdb)
    return {"message": "Delete TV Show endpoint hit", "imdb": imdb}


@app.patch("/api/{imdb}/edit/tv_show/status/{new_status}")
async def __update_tv_show_status(
    request: Request, imdb: str = Path(...), new_status: str = Path(...)
):
    update_tv_show_status(request, imdb, new_status)
    return {"message": "Status endpoint hit", "imdb": imdb, "new_status": new_status}


# ===============================================
# ============== TV SHOWS =======================
# ============== PROGRESS =======================
# ===============================================


@app.patch("/api/{imdb}/edit/tv_show/progress/{action}")
async def __update_tv_show_progress(
    request: Request, imdb: str = Path(...), action: str = Path(...)
):
    if action == "increment":
        increment_tv_show_progress(request, imdb)
    elif action == "decrement":
        decrement_tv_show_progress(request, imdb)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be 'increment' or 'decrement'.",
        )
    return {"message": "Progress endpoint hit", "imdb": imdb, "action": action}


@app.patch("/api/{imdb}/edit/tv_show/progress/by_index/{index}")
async def __update_by_index_tv_show_progress(
    request: Request, imdb: str = Path(...), index: str = Path(...)
):
    update_by_index_tv_show_progress(request, imdb, int(index))
    return {
        "message": "Progress endpoint hit",
        "imdb": imdb,
        "action": "update_by_index",
        "index": index,
    }


# ===============================================
# ============== MOVIES =========================
# ===============================================


@app.post("/api/movielist")
async def __get_user_movie_list(request: Request):
    data = get_user_movie_list(request)
    return {"watchlist": data}


@app.post("/api/movielist/{status}")
async def __get_user_movie_list_by_status(request: Request, status: str = Path(...)):
    print(f"TV LIST ROUTE HIT with status: {status}")
    data = get_user_movie_list_by_status(request, status)
    return {"watchlist": data}


@app.post("/api/add/movie")
async def __add_movie(request: Request, data: Movie):
    print(data)
    add_movie(request, data)
    return {"message": "Add Movie endpoint hit", "data": data}


@app.delete("/api/delete/{imdb}/movie")
async def __delete_movie(request: Request, imdb: str = Path(...)):
    delete_movie(request, imdb)
    return {"message": "Delete Movie endpoint hit", "imdb": imdb}


@app.patch("/api/{imdb}/edit/movie/status/{new_status}")
async def __update_movie_status(
    request: Request, imdb: str = Path(...), new_status: str = Path(...)
):
    update_movie_status(request, imdb, new_status)
    return {"message": "Status endpoint hit", "imdb": imdb, "new_status": new_status}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(PORT), reload=False)
