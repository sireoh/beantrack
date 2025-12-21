from sqlite3 import Date
from typing import List, Literal, Union
from pydantic import BaseModel


class Episode(BaseModel):
    code: str
    name: str


class TVShow(BaseModel):
    status: Literal["watching", "completed", "plan_to_watch"]
    image: str
    title: str
    imdb: str
    score: Union[float, str]
    currentEpisodeIndex: int
    episodes: List[Episode]


class Movie(BaseModel):
    status: Literal["watching", "completed", "plan_to_watch"]
    image: str
    title: str
    imdb: str
    score: Union[float, str]


class User(BaseModel):
    username: str
    password: str
