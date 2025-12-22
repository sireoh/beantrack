-- Create tables for BeanTrack app

-- Level 0: Independent tables (no foreign keys)
CREATE TABLE users
(
	user_id UUID PRIMARY KEY,
	username VARCHAR NOT NULL UNIQUE,
	password VARCHAR NOT NULL,
	user_type VARCHAR DEFAULT 'user',
	avatar VARCHAR
);

CREATE TABLE progress
(
	progress_id UUID PRIMARY KEY,
	status VARCHAR,
	current_episode_index INTEGER DEFAULT 0
);

CREATE TABLE episodelist
(
	episode_list_id UUID PRIMARY KEY
);

-- Level 1: Tables depending on Level 0
CREATE TABLE sessions
(
	session_id UUID PRIMARY KEY,
	user_id UUID REFERENCES users(user_id),
	refresh_token_hash VARCHAR,
	device_type VARCHAR,
	ip_address VARCHAR,
	last_active_at TIMESTAMP,
	expires_at TIMESTAMP,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tvlist
(
	tv_list_id UUID PRIMARY KEY,
	user_id UUID REFERENCES users(user_id)
);

CREATE TABLE movielist
(
	movie_list_id UUID PRIMARY KEY,
	user_id UUID REFERENCES users(user_id)
);

-- Level 2: Tables depending on Level 0 and/or Level 1
CREATE TABLE tvshow
(
	imdb VARCHAR PRIMARY KEY,
	tv_list_id UUID REFERENCES tvlist(tv_list_id),
	title VARCHAR,
	image VARCHAR,
	score FLOAT,
	episode_list_id UUID REFERENCES episodelist(episode_list_id),
	progress_id UUID REFERENCES progress(progress_id)
);

CREATE TABLE movie
(
	imdb VARCHAR PRIMARY KEY,
	movie_list_id UUID REFERENCES movielist(movie_list_id),
	title VARCHAR,
	image VARCHAR,
	score FLOAT,
	progress_id UUID REFERENCES progress(progress_id)
);

CREATE TABLE episode
(
	episode_id VARCHAR PRIMARY KEY,
	episode_list_id UUID REFERENCES episodelist(episode_list_id),
	name VARCHAR,
	season INTEGER,
	number INTEGER
);