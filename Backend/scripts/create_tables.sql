-- Create tables for BeanTrack app

-- Users table
CREATE TABLE users
(
	userId UUID PRIMARY KEY,
	username VARCHAR NOT NULL UNIQUE,
	password VARCHAR NOT NULL,
	userType VARCHAR DEFAULT 'user',
	avatar VARCHAR
);

-- Sessions table
CREATE TABLE sessions
(
	sessionId UUID PRIMARY KEY,
	userId UUID REFERENCES users(userId),
	refreshTokenHash VARCHAR,
	deviceType VARCHAR,
	IPAddress VARCHAR,
	lastActiveAt TIMESTAMP,
	expiresAt TIMESTAMP,
	createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Progress table
CREATE TABLE progress
(
	progressId UUID PRIMARY KEY,
	status VARCHAR,
	currentEpisodeIndex INTEGER DEFAULT 0
);

-- TVList table
CREATE TABLE tvlist
(
	tvListId UUID PRIMARY KEY,
	userId UUID REFERENCES users(userId)
);

-- EpisodeList table
CREATE TABLE episodelist
(
	episodeListId UUID PRIMARY KEY
);

-- TVShow table
CREATE TABLE tvshow
(
	imdb VARCHAR PRIMARY KEY,
	tvListId UUID REFERENCES tvlist(tvListId),
	title VARCHAR,
	image VARCHAR,
	score FLOAT,
	episodeListId UUID REFERENCES episodelist(episodeListId),
	progressId UUID REFERENCES progress(progressId)
);

-- Episode table
CREATE TABLE episode
(
	episodeId VARCHAR PRIMARY KEY,
	episodeListId UUID REFERENCES episodelist(episodeListId),
	name VARCHAR,
	code VARCHAR
);

-- MovieList table
CREATE TABLE movielist
(
	movieListId UUID PRIMARY KEY,
	userId UUID REFERENCES users(userId)
);

-- Movie table
CREATE TABLE movie
(
	imdb VARCHAR PRIMARY KEY,
	movieListId UUID REFERENCES movielist(movieListId),
	title VARCHAR,
	image VARCHAR,
	score FLOAT,
	progressId UUID REFERENCES progress(progressId)
);