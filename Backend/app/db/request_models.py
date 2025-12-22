from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    imdb: str
    new_status: str


class UpdateProgressRequest(BaseModel):
    imdb: str


class UpdateProgressByIndexRequest(BaseModel):
    imdb: str
    index: int
