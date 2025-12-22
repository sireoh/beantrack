from sqlalchemy import Column, String, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()


# ===============================================
# ============== SQLAlchemy MODELS ==============
# ===============================================


class DBUser(Base):
    __tablename__ = "users"
    userId = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String)
    password = Column(String)
    userType = Column(String)
    avatar = Column(String)


class DBSession(Base):
    __tablename__ = "sessions"
    sessionId = Column(UUID(as_uuid=True), primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))
    refreshTokenHash = Column(String)
    deviceType = Column(String)
    IPAddress = Column(String)
    lastActiveAt = Column(TIMESTAMP)
    expiresAt = Column(TIMESTAMP)
    createdAt = Column(TIMESTAMP, default=datetime.utcnow)


class DBProgress(Base):
    __tablename__ = "progress"
    progressId = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(String)
    currentEpisodeIndex = Column(Integer)


class DBTVList(Base):
    __tablename__ = "tvlist"
    tvListId = Column(UUID(as_uuid=True), primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))


class DBEpisodeList(Base):
    __tablename__ = "episodelist"
    episodeListId = Column(UUID(as_uuid=True), primary_key=True)


class DBTVShow(Base):
    __tablename__ = "tvshow"
    imdb = Column(String, primary_key=True)
    tvListId = Column(UUID(as_uuid=True), ForeignKey("tvlist.tvListId"))
    title = Column(String)
    image = Column(String)
    score = Column(Float)
    episodeListId = Column(UUID(as_uuid=True), ForeignKey("episodelist.episodeListId"))
    progressId = Column(UUID(as_uuid=True), ForeignKey("progress.progressId"))


class DBEpisode(Base):
    __tablename__ = "episode"
    episodeId = Column(String, primary_key=True)  # Assuming varchar
    episodeListId = Column(UUID(as_uuid=True), ForeignKey("episodelist.episodeListId"))
    name = Column(String)
    code = Column(String)


class DBMovieList(Base):
    __tablename__ = "movielist"
    movieListId = Column(UUID(as_uuid=True), primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))


class DBMovie(Base):
    __tablename__ = "movie"
    imdb = Column(String, primary_key=True)
    movieListId = Column(UUID(as_uuid=True), ForeignKey("movielist.movieListId"))
    title = Column(String)
    image = Column(String)
    score = Column(Float)
    progressId = Column(UUID(as_uuid=True), ForeignKey("progress.progressId"))


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
