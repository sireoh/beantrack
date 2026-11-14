# BeanTrack

TV show and movie tracker: FastAPI backend (`backend/`) and SvelteKit frontend (`frontend/`).
See each folder's README for development. This file covers running it with Docker.

## Docker

Two images, published as tags of one GHCR package:

| Image | What it is |
|---|---|
| `ghcr.io/sireoh/beantrack:backend` (`backend-<version>`) | FastAPI + SQLite, migrations on start, Litestream replication to B2 when configured |
| `ghcr.io/sireoh/beantrack:frontend` (`frontend-<version>`) | nginx serving the pre-built static site and proxying `/api` to the backend |

The browser only talks to the frontend container: the site calls the relative `/api`, and nginx
forwards it to the backend. So the same images work on any host; only `.env` changes.

All configuration is in the root `.env` (copy `.env.example`); compose passes it to the
containers. Nothing is baked into the images.

### Build the frontend (on your machine)

SvelteKit bakes `PUBLIC_*` values into the build, so use the `docker` mode: its
`frontend/.env.docker` overrides `PUBLIC_API_URL` with an empty value, whatever your dev
`frontend/.env` says, and the site then calls `/api` on whatever host serves it.

```bash
cd frontend
npm run build:docker
```

### Build and push the images

Log in to GHCR once with a GitHub personal access token that has the `write:packages` scope
(paste the token at the password prompt):

```bash
docker login ghcr.io -u sireoh
```

From the repo root (set the version to whatever you are releasing):

```bash
docker buildx build --platform linux/amd64 --push -t ghcr.io/sireoh/beantrack:backend -t ghcr.io/sireoh/beantrack:backend-0.1.0 ./backend
```

```bash
docker buildx build --platform linux/amd64 --push -t ghcr.io/sireoh/beantrack:frontend -t ghcr.io/sireoh/beantrack:frontend-0.1.0 ./frontend
```

### Run

```bash
cp .env.example .env
```

Fill in `.env`, then:

```bash
docker compose pull
```

```bash
docker compose up -d
```

The site is on `FRONTEND_PUBLISH` (default http://localhost:8080). To run from local source
instead of GHCR: `docker compose up -d --build`. Logs: `docker compose logs -f backend`.

The server only needs `docker-compose.yml` and `.env`, not the source code.

### Behind your reverse proxy (https://beantrack.vincefung.cc)

Both containers publish a port on the host: the site on `FRONTEND_PUBLISH` (default 8080) and
the API on `BACKEND_PUBLISH` (default 8000). Point your proxy at the site port; the site's own
nginx already forwards `/api` to the backend, so the API port is optional for the proxy. Then set:

```
FRONTEND_URL=https://beantrack.vincefung.cc/
DISCORD_REDIRECT_URI=https://beantrack.vincefung.cc/api/auth/callback
CORS_ORIGINS=["https://beantrack.vincefung.cc"]
COOKIE_SECURE=true
```

Register the same redirect URI in the Discord developer portal. TLS is your proxy's job.

### Data, Litestream and backups

- The database is on the `DATA_VOLUME` volume (`/app/data` in the container), so it survives
  image updates. A host path also works; make it owned by uid 10001 first.
- With the `B2_*` values set (and `LITESTREAM_ENABLED=true`), the backend runs under
  `litestream replicate`. On a fresh server with an empty volume it first restores the
  database from the replica. Without them it starts normally.
- Manual backups/restores (Settings → Admin) use the same B2 key and work with or without
  Litestream.

### Pulling a private package on the server

GHCR packages start private. Either make it public (GitHub → your profile → Packages →
beantrack → Package settings → Change visibility), or log in on the server with a token that
has `read:packages`:

```bash
docker login ghcr.io -u sireoh
```
