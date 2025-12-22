"""
Search data access layer for external APIs.
"""

from fastapi import Request
import httpx
from app.core.config import settings

OMDB_API_KEY = settings.omdb_api_key


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
            url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "omdb"}


async def search_tv_show_by_tvmaze_id(id: str):
    """
    Get episodes for a TV show by TVMaze ID.

    :param id: The TVMaze ID.
    :return: JSON response from TVMaze API.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.tvmaze.com/shows/{id}/episodes"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "tvmaze"}


async def search_movie_by_imdb_id(imdb: str):
    """
    Get movie details by IMDB ID using OMDB API.

    :param imdb: The IMDB ID.
    :return: JSON response from OMDB API.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "omdb"}
