"""
Search data access layer for external APIs.
"""

import httpx
from app.core.config import settings


async def search_tv_show(query: str):
    """
    Search for TV shows using TVMaze API.

    :param query: The search query.
    :return: JSON response from TVMaze API.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.tvmaze.com/search/shows?q={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "tvmaze"}


async def search_movie(query: str):
    """
    Search for movies using OMDB API.

    :param query: The search query.
    :return: JSON response from OMDB API.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://www.omdbapi.com/?apikey={settings.omdb_api_key}&s={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "omdb"}
