from sqlalchemy import Column, String, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()


# ===============================================
# ============== SQLAlchemy MODELS ==============
# ===============================================


class DBUser(Base):
    __tablename__ = "users"
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    user_type: Mapped[str] = mapped_column(String)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DBSession(Base):
    __tablename__ = "sessions"
    session_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id")
    )
    refresh_token_hash: Mapped[str] = mapped_column(String)
    device_type: Mapped[str] = mapped_column(String)
    ip_address: Mapped[str] = mapped_column(String)
    last_active_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)


class DBProgress(Base):
    __tablename__ = "progress"
    progress_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String)
    current_episode_index: Mapped[int] = mapped_column(Integer, default=0)


class DBTVList(Base):
    __tablename__ = "tvlist"
    tv_list_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id")
    )


class DBEpisodeList(Base):
    __tablename__ = "episodelist"
    episode_list_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)


class DBTVShow(Base):
    __tablename__ = "tvshow"
    imdb: Mapped[str] = mapped_column(String, primary_key=True)
    tv_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tvlist.tv_list_id")
    )
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    episode_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodelist.episode_list_id")
    )
    progress_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progress.progress_id")
    )


class DBEpisode(Base):
    __tablename__ = "episode"
    episode_id: Mapped[str] = mapped_column(String, primary_key=True)
    episode_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodelist.episode_list_id")
    )
    name: Mapped[str] = mapped_column(String)
    season: Mapped[int] = mapped_column(Integer)
    number: Mapped[int] = mapped_column(Integer)


class DBMovieList(Base):
    __tablename__ = "movielist"
    movie_list_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id")
    )


class DBMovie(Base):
    __tablename__ = "movie"
    imdb: Mapped[str] = mapped_column(String, primary_key=True)
    movie_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("movielist.movie_list_id")
    )
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    progress_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progress.progress_id")
    )


# ===============================================
# ============== PYDANTIC MODELS ================
# ===============================================


class User(BaseModel):
    userId: Optional[str] = None
    username: str
    password: str
    userType: Optional[str] = "user"
    avatar: Optional[str] = None


class TVShow(BaseModel):
    imdb: str
    title: str
    image: Optional[str] = None
    score: Optional[float] = None


class Movie(BaseModel):
    imdb: str
    title: str
    image: Optional[str] = None
    score: Optional[float] = None


class Episode(BaseModel):
    imdb: str
    name: str
    season: int
    number: int


# ===============================================
# ======= PYDANTIC MODELS : REQUEST MODELS ======
# ===============================================


class SignupRequest(BaseModel):
    username: str
    password: str


class UpdateStatusRequest(BaseModel):
    imdb: str
    status: str


class UpdateProgressRequest(BaseModel):
    imdb: str


class UpdateProgressByIndexRequest(BaseModel):
    imdb: str
    index: int


class AddTVShowRequest(BaseModel):
    tvmaze_id: int
    status: str


class AddMovieRequest(BaseModel):
    imdb: str
    status: str


class MovieData(BaseModel):
    title: str
    image: Optional[str]
    imdb: str
    score: Optional[float]


class EpisodeData(BaseModel):
    episode_id: str
    name: str
    season: int
    number: int


class TVShowData(BaseModel):
    title: str
    image: Optional[str]
    imdb: Optional[str]
    score: Optional[float]
    episodes: List[EpisodeData]
