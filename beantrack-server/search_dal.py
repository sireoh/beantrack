import os
from fastapi import Request
import httpx

OMDB_API_KEY = os.environ["OMDB_API_KEY"]


async def search_tv_show(query: str):
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.tvmaze.com/search/shows?q={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "tvmaze"}


async def search_movie(query: str):
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "omdb"}


async def search_tv_show_by_tvmaze_id(query: str):
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.tvmaze.com/search/shows?q={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "tvmaze"}


async def search_movie_by_imdb(query: str):
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
            res = await client.get(url)
            return res.json()
        except Exception as e:
            return {"error": str(e), "source": "omdb"}
