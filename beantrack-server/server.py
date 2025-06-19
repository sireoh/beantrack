from dotenv import load_dotenv
import uvicorn
from fastapi import Cookie, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Path
from helpers import Helpers
from models import TVShow, User
from sessions_dal import add_session, delete_session
from tvlist_dal import (
    add_tv_show,
    decrement_progress,
    increment_progress,
    update_status,
)
from user_dal import add_user, delete_user
import os

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:your-client-port"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
DEBUG = os.environ["DEBUG"] == "true"

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
async def __login(data: User, response: Response):
    _r = add_session(data)

    if _r.get("is_logged_in"):
        return {"message": "User is already logged in", "data": data}

    session_id = _r["session_id"]
    signed_session = Helpers.sign_session_id(session_id)

    response.set_cookie(
        key="session_token",
        value=signed_session,
        httponly=True,  # Prevents JS access
        secure=True if not DEBUG else False,  # Only sent over HTTPS
        samesite="lax",  # Good default; prevents CSRF in most cases
        max_age=60 * 60 * 24,  # 1 day, Gets restored when browser comes back anyways
    )

    return {"message": "User logged in", "data": data}


@app.post("/api/logout")
async def __logout(response: Response, session_token: str = Cookie(None)):
    return delete_session(response, session_token)


# ===============================================
# ============== AUTH ===========================
# ===============================================

# ===============================================
# ============== TV SHOWS =======================
# ===============================================


@app.post("/api/add/tv_show")
async def __add_tv_show(data: TVShow):
    print(data)
    add_tv_show(data)
    return {"message": "Add TV Show endpoint hit", "data": data}


@app.patch("/api/{imdb}/edit/status/{new_status}")
async def __update_status(imdb: str = Path(...), new_status: str = Path(...)):
    update_status(imdb, new_status)
    return {"message": "Status endpoint hit", "imdb": imdb, "new_status": new_status}


@app.patch("/api/{imdb}/edit/progress/{action}")
async def __update_progress(imdb: str = Path(...), action: str = Path(...)):
    if action == "increment":
        increment_progress(imdb)
    elif action == "decrement":
        decrement_progress(imdb)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be 'increment' or 'decrement'.",
        )
    return {"message": "Progress endpoint hit", "imdb": imdb, "action": action}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=False)
