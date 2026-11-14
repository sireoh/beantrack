# BeanTrack backend

FastAPI + SQLAlchemy 2.0 + SQLite (WAL) API for tracking TV shows and movies.
Login is Discord OAuth2; the database is replicated continuously to Backblaze B2 with Litestream.

## Architecture

```
backend/
├── app/
│   ├── main.py               # create_app(): wires settings, DB, HTTP client, routers under /api
│   ├── core/                 # no FastAPI/DB knowledge
│   │   ├── config.py         # Settings (pydantic-settings) loaded from .env
│   │   ├── security.py       # session-token hashing, Fernet TokenCipher
│   │   ├── errors.py         # AppError hierarchy (404/409/422/401/502)
│   │   └── ids.py            # uuid4 ids
│   ├── db/
│   │   ├── base.py           # DeclarativeBase + constraint naming convention
│   │   ├── session.py        # engine (WAL, busy_timeout, foreign_keys) + sessionmaker
│   │   └── types.py          # UTCDateTime column type
│   ├── models/               # SQLAlchemy ORM models (Mapped[...])
│   ├── schemas/              # Pydantic v2 request/response models (the API contract)
│   ├── repositories/         # CRUD queries; take a Session, never commit
│   ├── clients/              # typed httpx wrappers: TVmaze, OMDb, Discord
│   ├── services/             # use cases (login, add show…); own the transaction
│   └── api/
│       ├── deps.py           # Depends() providers + Annotated aliases (CurrentUser, DbSession…)
│       └── routers/          # auth, tvlist, movielist, search
├── migrations/               # Alembic (env.py reads the DB path from Settings)
├── testing/                  # pytest suite + fake upstream APIs
├── alembic.ini
├── litestream.yml
├── pyproject.toml
└── .env.example
```

Requests flow one way: **router → service → repository / client → model**.

- **Routers** only do HTTP: parse input with a schema, call one service function, serialise the
  result. They stay thin enough to read at a glance.
- **Services** hold the rules (e.g. "fetch a show from TVmaze only the first time anyone adds it",
  "the current episode must belong to the show") and decide when to commit. They raise
  `AppError`s instead of `HTTPException`, so they can be reused outside HTTP (scripts, jobs).
- **Repositories** are the only place that writes SQL, so query tuning (eager loading,
  `ON CONFLICT`) is in one place.
- **Clients** isolate each external API behind a typed method. They all share one `httpx.Client`
  that `create_app()` accepts as a parameter, which is how the tests swap in a mock transport.
- **Schemas vs models** are separate on purpose: the database shape can change without breaking
  the API, and secrets (encrypted Discord tokens) can never leak into a response by accident.

### Data model

Show and movie data is stored once and shared by everyone (`tvshows`, `episodes`, `movies`);
each user only stores their own progress (`user_tvshows`, `user_movies`).

```
users ─1:1─ tvlists ─1:n─ user_tvshows ─n:1─ tvshows ─1:n─ episodes
      ─1:1─ movielists ─1:n─ user_movies ─n:1─ movies
      ─1:n─ sessions
```

Additions beyond the base spec, and why:

| Column | Why |
|---|---|
| `users.discord_access_token`, `discord_refresh_token`, `discord_token_expires_at` | Where the Fernet-encrypted Discord tokens live |
| `tvshows.tvmaze_id` | Lets episodes be re-fetched without another IMDb lookup |
| `episodes.number` nullable | TVmaze specials have no episode number |

`sessions.session_id` is the SHA-256 of the cookie token; the raw token is never stored.

## API

All routes are under `/api`. Interactive docs: http://localhost:8000/docs

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/api/auth/login` | – | Redirects to Discord |
| GET | `/api/auth/callback` | – | Discord redirects here; sets the `beantrack_session` cookie |
| POST | `/api/auth/logout` | – | Deletes the session |
| GET | `/api/auth/me` | ✔ | Current user |
| POST | `/api/auth/profile/refresh` | ✔ | Refresh username and avatar from Discord |
| GET | `/api/tvlist` | ✔ | Full TV list |
| POST | `/api/tvlist/add` | ✔ | `{"show": {"imdb": "tt0903747", "tvmaze_id": 169, "title": "Breaking Bad", "image": "...", "score": 9.2}, "status": "watching"}` |
| GET | `/api/tvlist/{imdb}/episodes` | ✔ | Return the cached episodes for a TV show |
| PATCH | `/api/tvlist/{imdb}/progress` | ✔ | Update clamped episode progress and current episode metadata |
| PATCH | `/api/tvlist/{imdb}/status` | ✔ | `{"status": "watching"}` |
| DELETE | `/api/tvlist/{imdb}` | ✔ | Remove a show from the current user's list |
| GET | `/api/movielist` | ✔ | Full movie list |
| POST | `/api/movielist/add` | ✔ | `{"movie": {"imdb": "tt0133093", "title": "The Matrix", "image": "..."}, "status": "planned"}` |
| PATCH | `/api/movielist/{imdb}/status` | ✔ | `{"status": "completed"}` |
| DELETE | `/api/movielist/{imdb}` | ✔ | Remove a movie from the current user's list |
| GET | `/api/search?type=tv\|movie&q=` | ✔ | TVmaze for `tv`, OMDb for `movie` |
| GET | `/api/health` | – | Liveness |

`status` is one of `watching | completed | planned | dropped` (default `planned`).
`current_episode` is a zero-based index into the cached episode list and defaults to `0`. Adding
something already on your list returns 409. The add endpoint stores the supplied show metadata,
then synchronously fetches and caches episodes from TVmaze with
`/shows/{tvmaze_id}?embed=episodes`. The response includes `episodes_count` rather than the full
episode list. Progress updates accept exactly one of `set_to` or `delta`, plus the required
`current_episode_metadata` episode object, for example
`{"id": 1874762, "season": 1, "number": 1, "title": "Pilot", "image": "..."}`.

Movie ratings are fetched from OMDb only when `/api/movielist/add` first inserts
the shared movie catalog row. OMDb's `imdbRating` is stored and returned as `score`;
later users reuse the cached value without another detail request.

## Running locally

Requires Python 3.12+. Commands are run from `backend/`.

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `.env` (set `COOKIE_SECURE=false` for plain-http local dev), then create the database
and start the server:

```bash
uv run alembic upgrade head
```

```bash
uv run uvicorn app.main:create_app --factory --reload
```

```bash
python -m uvicorn app.main:create_app --factory --reload
```

With plain pip instead of uv:

```bash
python -m venv .venv && . .venv/bin/activate && pip install -e . pytest
```

### Migrations

After changing a model:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Review the generated file in `migrations/versions/`, then `uv run alembic upgrade head`.
SQLite can't `ALTER` most things, so migrations run in batch mode (table copy + swap).

## Tests

```bash
uv run pytest
```

Each test gets a fresh SQLite file in a temp directory, and TVmaze, OMDb and Discord are replaced
by `testing/fakes.py` through `httpx.MockTransport`, so no network access or real keys are needed.
The suite covers the list and search endpoints, 401s on every protected route, isolation between
users, the full OAuth callback (token encryption, hashed sessions, list creation), and a check that
the Alembic migration produces exactly the schema the models describe.

Type-check with `uv run mypy`.

## Backups (Litestream → Backblaze B2)

1. In B2, create a **private** bucket and an application key restricted to it. Put the key id,
   key, bucket name and the bucket's S3 endpoint into `.env`.
2. Install Litestream on the server (https://litestream.io/install/).
3. Run the API under Litestream, so replication starts first and stops last:

```bash
set -a; . ./.env; set +a
```

```bash
litestream replicate -config litestream.yml -exec "uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"
```

```shell
litestream replicate `
  -config .\litestream.yml `
  -exec "python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000"
```

Litestream ships WAL changes to B2 every few seconds. Run `alembic upgrade head` before starting
it on a new server. In production, run this under systemd (or similar) with the env file loaded.

### Restore

Stop the app, then restore the latest replica into the data folder:

```bash
set -a; . ./.env; set +a
```

```bash
litestream restore -config litestream.yml -if-db-not-exists "$DATA_DIR/$DATABASE_NAME"
```

To restore to a point in time instead, add `-timestamp 2026-11-13T12:00:00Z`, or restore to a
different file with `-o restored.db` to inspect it first.

**Keep `ENCRYPTION_KEY` backed up separately** (e.g. in a password manager). Without it the
restored Discord tokens can't be decrypted; everything else still works and users simply log in again.

### Notes on SQLite

- WAL mode, `busy_timeout=5000`, `synchronous=NORMAL` and `foreign_keys=ON` are set on every
  connection (`app/db/session.py`).
- Don't copy `beantrack.db` while the app is running without its `-wal` file; use the Litestream
  replica or `sqlite3 data/beantrack.db ".backup copy.db"`.
- Run a single uvicorn worker process per database file. SQLite allows one writer at a time;
  that's plenty for this app, and the busy timeout absorbs short waits.
