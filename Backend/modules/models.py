from typing import List, Literal, Union
from pydantic import BaseModel


# ===============================================
# ============== DATA MODELS ====================
# ===============================================


class Episode(BaseModel):
    """
    Represents an episode of a TV show.

    Attributes:
        code (str): The episode code (e.g., S01E01).
        name (str): The episode name.
    """

    code: str
    name: str


class TVShow(BaseModel):
    """
    Represents a TV show in the user's watchlist.

    Attributes:
        status (Literal): The watch status.
        image (str): URL to the show's image.
        title (str): The show title.
        imdb (str): IMDb ID.
        score (Union[float, str]): User's score.
        currentEpisodeIndex (int): Current episode index.
        episodes (List[Episode]): List of episodes.
    """

    status: Literal["watching", "completed", "plan_to_watch"]
    image: str
    title: str
    imdb: str
    score: Union[float, str]
    currentEpisodeIndex: int
    episodes: List[Episode]


class Movie(BaseModel):
    """
    Represents a movie in the user's watchlist.

    Attributes:
        status (Literal): The watch status.
        image (str): URL to the movie's image.
        title (str): The movie title.
        imdb (str): IMDb ID.
        score (Union[float, str]): User's score.
    """

    status: Literal["watching", "completed", "plan_to_watch"]
    image: str
    title: str
    imdb: str
    score: Union[float, str]


class User(BaseModel):
    """
    Represents a user.

    Attributes:
        username (str): The username.
        password (str): The password.
    """

    username: str
    password: str


# ===============================================
# ============== REQUEST MODELS =================
# ===============================================


class UpdateStatusRequest(BaseModel):
    """
    Request model for updating status.

    Attributes:
        imdb (str): IMDb ID.
        new_status (str): New status.
    """

    imdb: str
    new_status: str


class DeleteRequest(BaseModel):
    """
    Request model for deletion.

    Attributes:
        imdb (str): IMDb ID.
    """

    imdb: str


class UpdateProgressRequest(BaseModel):
    """
    Request model for updating progress.

    Attributes:
        imdb (str): IMDb ID.
    """

    imdb: str


class UpdateProgressByIndexRequest(BaseModel):
    """
    Request model for updating progress by index.

    Attributes:
        imdb (str): IMDb ID.
        index (int): New index.
    """

    imdb: str
    index: int
