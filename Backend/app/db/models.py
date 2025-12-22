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
    userid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    usertype: Mapped[str] = mapped_column(String)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DBSession(Base):
    __tablename__ = "sessions"
    sessionid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    userid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.userid"))
    refreshtokenhash: Mapped[str] = mapped_column(String)
    devicetype: Mapped[str] = mapped_column(String)
    ipaddress: Mapped[str] = mapped_column(String)
    lastactiveat: Mapped[datetime] = mapped_column(TIMESTAMP)
    expiresat: Mapped[datetime] = mapped_column(TIMESTAMP)
    createdat: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)


class DBProgress(Base):
    __tablename__ = "progress"
    progressid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String)
    currentepisodeindex: Mapped[int] = mapped_column(Integer)


class DBTVList(Base):
    __tablename__ = "tvlist"
    tvlistid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    userid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.userid"))


class DBEpisodeList(Base):
    __tablename__ = "episodelist"
    episodelistid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)


class DBTVShow(Base):
    __tablename__ = "tvshow"
    imdb: Mapped[str] = mapped_column(String, primary_key=True)
    tvlistid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tvlist.tvlistid")
    )
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    episodelistid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodelist.episodelistid")
    )
    progressid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progress.progressid")
    )


class DBEpisode(Base):
    __tablename__ = "episode"
    episodeid: Mapped[str] = mapped_column(String, primary_key=True)  # Assuming varchar
    episodelistid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodelist.episodelistid")
    )
    name: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String)


class DBMovieList(Base):
    __tablename__ = "movielist"
    movielistid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    userid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.userid"))


class DBMovie(Base):
    __tablename__ = "movie"
    imdb: Mapped[str] = mapped_column(String, primary_key=True)
    movielistid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("movielist.movielistid")
    )
    title: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    progressid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progress.progressid")
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


class SignupRequest(BaseModel):
    username: str
    password: str


class UpdateStatusRequest(BaseModel):
    imdb: str
    new_status: str


class UpdateProgressRequest(BaseModel):
    imdb: str


class UpdateProgressByIndexRequest(BaseModel):
    imdb: str
    index: int
