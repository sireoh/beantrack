from sqlalchemy import Column, String, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()


# ===============================================
# ============== SQLAlchemy MODELS ==============
# ===============================================


class DBUser(Base):
    __tablename__ = "users"
    userId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    userType: Mapped[str] = mapped_column(String)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DBSession(Base):
    __tablename__ = "sessions"
    sessionId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    userId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.userId"))
    refreshTokenHash: Mapped[str] = mapped_column(String)
    deviceType: Mapped[str] = mapped_column(String)
    IPAddress: Mapped[str] = mapped_column(String)
    lastActiveAt: Mapped[datetime] = mapped_column(TIMESTAMP)
    expiresAt: Mapped[datetime] = mapped_column(TIMESTAMP)
    createdAt: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)


class DBProgress(Base):
    __tablename__ = "progress"
    progressId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String)
    currentEpisodeIndex: Mapped[int] = mapped_column(Integer)


class DBTVList(Base):
    __tablename__ = "tvlist"
    tvListId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    userId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.userId"))


class DBEpisodeList(Base):
    __tablename__ = "episodelist"
    episodeListId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)


class DBTVShow(Base):
    __tablename__ = "tvshow"
    imdb: Mapped[str] = mapped_column(String, primary_key=True)
    tvListId: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tvlist.tvListId")
    )
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    episodeListId: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodelist.episodeListId")
    )
    progressId: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progress.progressId")
    )


class DBEpisode(Base):
    __tablename__ = "episode"
    episodeId: Mapped[str] = mapped_column(String, primary_key=True)  # Assuming varchar
    episodeListId: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodelist.episodeListId")
    )
    name: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String)


class DBMovieList(Base):
    __tablename__ = "movielist"
    movieListId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    userId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.userId"))


class DBMovie(Base):
    __tablename__ = "movie"
    imdb: Mapped[str] = mapped_column(String, primary_key=True)
    movieListId: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("movielist.movieListId")
    )
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    progressId: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progress.progressId")
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


# ===============================================
# ======= PYDANTIC MODELS : REQUEST MODELS ======
# ===============================================


class UpdateStatusRequest(BaseModel):
    imdb: str
    new_status: str


class UpdateProgressRequest(BaseModel):
    imdb: str


class UpdateProgressByIndexRequest(BaseModel):
    imdb: str
    index: int
