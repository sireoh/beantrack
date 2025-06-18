import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Path
from models import TVShow
from tvlist_dal import (
    add_tv_show,
    decrement_progress,
    increment_progress,
    update_status,
)

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:your-client-port"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
