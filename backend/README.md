# BeanTrack backend

FastAPI + SQLAlchemy 2.0 + SQLite (WAL) API for tracking TV shows and movies.
Login is Discord OAuth2; the database is backed up to Backblaze B2 once a day (and on demand).

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
| PATCH | `/api/tvlist/{imdb}/progress` | ✔ | Update clamped episode progress and current episode metadata; also syncs status (see below) in the same commit |
| PATCH | `/api/tvlist/{imdb}/status` | ✔ | `{"status": "watching"}` |
| DELETE | `/api/tvlist/{imdb}` | ✔ | Remove a show from the current user's list |
| GET | `/api/movielist` | ✔ | Full movie list |
| POST | `/api/movielist/add` | ✔ | `{"movie": {"imdb": "tt0133093", "title": "The Matrix", "image": "..."}, "status": "planned"}` |
| PATCH | `/api/movielist/{imdb}/status` | ✔ | `{"status": "completed"}` |
| DELETE | `/api/movielist/{imdb}` | ✔ | Remove a movie from the current user's list |
| GET | `/api/search?type=tv\|movie&q=` | ✔ | TVmaze for `tv`, OMDb for `movie` |
| GET | `/api/discover/tv?page=N` | – | Popular shows from TMDB (`page` 1–500), cached per page in SQLite |
| GET | `/api/discover/movies?page=N` | – | Popular movies from TMDB, cached the same way |
| POST | `/api/discover/tv/add` | ✔ | `{"tmdb_id": 1396, "status": "watching"}`: TMDB → IMDb id → TVmaze, then the normal TV add |
| POST | `/api/discover/movies/add` | ✔ | `{"tmdb_id": 603}`: TMDB → IMDb id → OMDb, then the normal movie add |
| GET | `/api/auth/profile/export` | ✔ | Download your list entries (no show/movie metadata) |
| PATCH | `/api/auth/profile/theme` | ✔ | `{"theme": "dark"}` (`light` or `dark`); saved on the account |
| POST | `/api/auth/profile/import` | ✔ | Body: an export file. Adds missing entries, returns `{imported, skipped, failed, failures}` |
| POST | `/api/admin/backup` | admin | Snapshot the database (`VACUUM INTO`) and upload it to B2 |
| GET | `/api/admin/backups` | admin | Manual backups, newest first (each has a B2 file `id`) |
| DELETE | `/api/admin/backups/{id}` | admin | Delete one manual backup; files outside `manual-backups/` are never touched |
| POST | `/api/admin/restore` | admin | `{"name": "manual-backups/…"}`; uploads a safety backup, then restores |
| DELETE | `/api/admin/discover-cache` | admin | Empty both Discover cache tables |
| GET | `/api/health` | – | Liveness |

`status` is one of `watching | completed | planned | dropped` (default `planned`).
Progress and status stay in sync (`services/lists.py`): reaching the last episode sets Completed; moving off the last episode of a Completed show sets Watching; setting Completed jumps to the last episode. Planned and Dropped are otherwise left alone.

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

### Discover (TMDB)

`TMDB_BEARER_TOKEN` (TMDB's "API Read Access Token") enables Discover; without it the discover
routes answer 400. Each page of `/discover/tv` and `/discover/movie` is stored in
`discovercache_tv` / `discovercache_movies` (one row per page: results JSON, `total_pages`,
`fetched_at`) and served from there while it is younger than `DISCOVER_CACHE_HOURS` (24). Older
pages are fetched again on the next request; if TMDB is down, the expired page is served instead
of an error. TMDB never returns pages above 500, so `total_pages` is capped there.

Discover results have no IMDb id. Adding one asks TMDB for it (`/tv/{id}/external_ids` or
`/movie/{id}`), then runs the same add as search, so the list entry is identical. The TMDB id is
then saved on the catalog row (`tvshows.tmdb_id` / `movies.tmdb_id`), and Discover results for
known titles carry their `imdb`, which the frontend uses to show "Added".

### Client IP

Each session stores the IP it logged in from (`sessions.ip_address`). Behind a reverse proxy the
connection comes from the proxy, so `X-Forwarded-For` (read right to left) or `X-Real-IP` is used,
but only when the request comes from an address in `FORWARDED_ALLOW_IPS`
(`app/core/client_ip.py`). In Docker, uvicorn uses the same variable for `--forwarded-allow-ips`.

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
uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
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

## Backups (Backblaze B2)

In B2, create a **private** bucket and an application key restricted to it, and put the key id,
key and bucket name into `.env` (`B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`). Leave them
empty to run without backups. Nothing else needs to be installed, so this works on Windows too.

Each backup uses SQLite's `VACUUM INTO` to write a consistent copy while the app keeps running,
gzips it and uploads it to `manual-backups/` in the bucket through B2's native API.

### Daily backup

While the API runs, a background thread takes one backup a day and keeps the newest few:

| Variable | Default | Meaning |
|---|---|---|
| `DAILY_BACKUP_ENABLED` | `true` | Turn the daily backup on or off |
| `DAILY_BACKUP_TIME` | `03:00` | Time of day, `HH:MM` |
| `DAILY_BACKUP_TIMEZONE` | `UTC` | IANA time zone name, e.g. `America/Vancouver`; daylight saving is handled |
| `DAILY_BACKUP_KEEP` | `7` | How many daily backups to keep; older ones are deleted |

Daily backups are named `…-daily.db.gz`. Only those are pruned; manual and pre-restore backups
are kept until you delete them. A run costs about 2 B2 Class C transactions (authorize + list),
far under the free tier's 2,500 a day; uploads and deletes are Class A, which is free. Run a
single uvicorn worker so the backup only runs once.

### Manual backups and restore

Admins can take on-demand backups from the Settings page or with `POST /api/admin/backup`, and
delete them with `DELETE /api/admin/backups/{id}`.

Restoring (`POST /api/admin/restore`) first uploads a `-pre-restore` snapshot of the current data,
then copies the chosen backup into the live database with SQLite's online backup API, so open
connections pick the change up. It refuses backups from a different Alembic schema revision.
Sessions are restored too, so you may need to log in again afterwards.

To restore by hand on a new server (no admin user yet), download a backup from the B2 web UI,
stop the app, then unpack it into the data folder:

```bash
gunzip -c beantrack-20261114T030000Z-xxxxxxxx-daily.db.gz > data/beantrack.db
```

**Keep `ENCRYPTION_KEY` backed up separately** (e.g. in a password manager). Without it the
restored Discord tokens can't be decrypted; everything else still works and users simply log in again.

### Roles

`users.role` is `user` (default) or `admin`. Every `/api/admin/*` route returns 403 for non-admins.
There is no UI for granting it; set it in the database:

```bash
sqlite3 data/beantrack.db "UPDATE users SET role = 'admin' WHERE discord_id = '<your id>';"
```

### Notes on SQLite

- WAL mode, `busy_timeout=5000`, `synchronous=NORMAL` and `foreign_keys=ON` are set on every
  connection (`app/db/session.py`).
- Don't copy `beantrack.db` while the app is running without its `-wal` file; take a backup
  or use `sqlite3 data/beantrack.db ".backup copy.db"`.
- Run a single uvicorn worker process per database file. SQLite allows one writer at a time;
  that's plenty for this app, and the busy timeout absorbs short waits.
