from sqlalchemy import Column, String, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# ===============================================
# ============== SQLAlchemy MODELS ==============
# ===============================================


class User(Base):
    __tablename__ = "users"
    userId = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String)
    password = Column(String)
    userType = Column(String)
    avatar = Column(String)


class Session(Base):
    __tablename__ = "sessions"
    sessionId = Column(UUID(as_uuid=True), primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))
    refreshTokenHash = Column(String)
    deviceType = Column(String)
    IPAddress = Column(String)
    lastActiveAt = Column(TIMESTAMP)
    expiresAt = Column(TIMESTAMP)
    createdAt = Column(TIMESTAMP, default=datetime.utcnow)


class Progress(Base):
    __tablename__ = "progress"
    progressId = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(String)
    currentEpisodeIndex = Column(Integer)


class TVList(Base):
    __tablename__ = "tvlist"
    tvListId = Column(UUID(as_uuid=True), primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))


class EpisodeList(Base):
    __tablename__ = "episodelist"
    episodeListId = Column(UUID(as_uuid=True), primary_key=True)


class TVShow(Base):
    __tablename__ = "tvshow"
    imdb = Column(String, primary_key=True)
    tvListId = Column(UUID(as_uuid=True), ForeignKey("tvlist.tvListId"))
    title = Column(String)
    image = Column(String)
    score = Column(Float)
    episodeListId = Column(UUID(as_uuid=True), ForeignKey("episodelist.episodeListId"))
    progressId = Column(UUID(as_uuid=True), ForeignKey("progress.progressId"))


class Episode(Base):
    __tablename__ = "episode"
    episodeId = Column(String, primary_key=True)  # Assuming varchar
    episodeListId = Column(UUID(as_uuid=True), ForeignKey("episodelist.episodeListId"))
    name = Column(String)
    code = Column(String)


class MovieList(Base):
    __tablename__ = "movielist"
    movieListId = Column(UUID(as_uuid=True), primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))


class Movie(Base):
    __tablename__ = "movie"
    imdb = Column(String, primary_key=True)
    movieListId = Column(UUID(as_uuid=True), ForeignKey("movielist.movieListId"))
    title = Column(String)
    image = Column(String)
    score = Column(Float)
    progressId = Column(UUID(as_uuid=True), ForeignKey("progress.progressId"))
