-- Create tables for BeanTrack app

-- Level 0: Independent tables (no foreign keys)
CREATE TABLE users
(
	userId UUID PRIMARY KEY,
	username VARCHAR NOT NULL UNIQUE,
	password VARCHAR NOT NULL,
	userType VARCHAR DEFAULT 'user',
	avatar VARCHAR
);

CREATE TABLE progress
(
	progressId UUID PRIMARY KEY,
	status VARCHAR,
	currentEpisodeIndex INTEGER DEFAULT 0
);

CREATE TABLE episodelist
(
	episodeListId UUID PRIMARY KEY
);

-- Level 1: Tables depending on Level 0
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

CREATE TABLE tvlist
(
	tvListId UUID PRIMARY KEY,
	userId UUID REFERENCES users(userId)
);

CREATE TABLE movielist
(
	movieListId UUID PRIMARY KEY,
	userId UUID REFERENCES users(userId)
);

-- Level 2: Tables depending on Level 0 and/or Level 1
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

CREATE TABLE movie
(
	imdb VARCHAR PRIMARY KEY,
	movieListId UUID REFERENCES movielist(movieListId),
	title VARCHAR,
	image VARCHAR,
	score FLOAT,
	progressId UUID REFERENCES progress(progressId)
);

CREATE TABLE episode
(
	episodeId VARCHAR PRIMARY KEY,
	episodeListId UUID REFERENCES episodelist(episodeListId),
	name VARCHAR,
	code VARCHAR
);