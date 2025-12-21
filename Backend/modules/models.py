from typing import List, Literal, Union
from pydantic import BaseModel


# ===============================================
# ============== DATA MODELS ====================
# ===============================================
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


# ===============================================
# ============== REQUEST MODELS =================
# ===============================================


class UpdateStatusRequest(BaseModel):
    imdb: str
    new_status: str


class DeleteRequest(BaseModel):
    imdb: str


class UpdateProgressRequest(BaseModel):
    imdb: str


class UpdateProgressByIndexRequest(BaseModel):
    imdb: str
    index: int
