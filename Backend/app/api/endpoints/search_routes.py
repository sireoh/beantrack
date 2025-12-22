from fastapi import APIRouter, HTTPException, Query, status

from app.services.search_service import (
    search_movie,
    search_tv_show,
)

search_router = APIRouter()


@search_router.get("/search/tv_show")
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


@search_router.get("/search/movie")
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
