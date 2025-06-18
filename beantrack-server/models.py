from typing import List, Literal
from pydantic import BaseModel


class Episode(BaseModel):
    code: str
    name: str


class TVShow(BaseModel):
    status: Literal["watching", "completed", "plan_to_watch"]
    image: str
    title: str
    imdb: str
    score: float
    currentEpisodeIndex: int
    episodes: List[Episode]
