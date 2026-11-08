# BeanTrack backend

Go + Echo API for BeanTrack. Users sign in with Discord (OAuth2), and each user
gets one TV list and one movie list. Data lives in SQLite (GORM with the
pure-Go `glebarez/sqlite` driver), and Litestream backs it up to Backblaze B2.

```
backend/
  cmd/server/main.go   entry point
  internal/config      env loading and validation
  internal/db          SQLite open, pragmas, migrations
  internal/models      GORM models
  internal/auth        Discord OAuth2, sessions, auth middleware
  internal/handlers    /api/me, /healthz
  internal/server      routes and middleware
  testing/             API tests (package apitest)
  litestream.yml       backup config
  .env.example
```

## Setup

1. Install Go 1.27 or newer.
2. Create an app at <https://discord.com/developers/applications>. Under
   **OAuth2**, add the redirect `http://localhost:8080/auth/discord/callback`
   (or whatever `DISCORD_REDIRECT_URI` you'll use), then copy the client ID
   and secret.
3. `cp .env.example .env` and fill it in (see below).

## Environment variables

The app reads its config from the environment. In development it also loads
`backend/.env`; values already in the real environment take precedence. If a
required variable is missing or invalid, it exits at startup and names every
problem.

| Variable | Required | Purpose |
|---|---|---|
| `PORT` | yes | HTTP port. The server listens on `0.0.0.0:$PORT`. |
| `DATA_DIR` | yes | Data folder. The DB is `$DATA_DIR/beantrack.db`; the folder is created if missing. Locally, use `../data` (git-ignored). |
| `DISCORD_CLIENT_ID` | yes | Discord OAuth2 client ID |
| `DISCORD_CLIENT_SECRET` | yes | Discord OAuth2 client secret |
| `DISCORD_REDIRECT_URI` | yes | OAuth2 callback URL. Must match the one registered with Discord. |
| `SESSION_SECRET` | yes | At least 32 characters. Signs cookies and encrypts the stored Discord tokens. Changing it logs everyone out. |
| `LOGIN_REDIRECT_URL` | no | Where the browser goes after login (default `/`) |
| `B2_BUCKET` | backups | B2 bucket name |
| `B2_ENDPOINT` | backups | S3 endpoint, e.g. `https://s3.us-west-004.backblazeb2.com` |
| `B2_REGION` | backups | Region from the endpoint, e.g. `us-west-004` |
| `B2_KEY_ID` | backups | B2 application key ID |
| `B2_APPLICATION_KEY` | backups | B2 application key |
| `LITESTREAM_ENCRYPTION_KEY` | backups | Base64 of 32 random bytes (`openssl rand -base64 32`) |

Litestream reads the backup variables; the app doesn't use them. The app
still checks them: leave all six empty to run without backups. If you set
any, you must set all six, and the key must decode to 32 bytes. This stops a
deploy that forgot the key from silently uploading unencrypted backups.

## Running locally

```bash
cd backend
go run ./cmd/server
```

Then open <http://localhost:8080/auth/discord/login>.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/healthz` | – | `{"status":"ok"}` when the DB is reachable, otherwise 503 |
| GET | `/auth/discord/login` | – | Redirects to Discord with a CSRF `state` |
| GET | `/auth/discord/callback` | – | Exchanges the code, creates or updates the user, sets the session cookie, redirects to `LOGIN_REDIRECT_URL` |
| POST | `/auth/logout` | cookie | Deletes the session and clears the cookie (204) |
| GET | `/api/me` | cookie | Current user's profile plus `tv_list_id` and `movie_list_id` |

Everything under `/api/*` requires a session and returns 401 without one.

### Auth details

- Scopes: `identify email`. The email is stored when Discord returns it, and
  it isn't overwritten if a later login has no email.
- The session cookie (`bt_session`) is `HttpOnly`, `Secure` and
  `SameSite=Lax`, and lasts 30 days. Its value is a random token plus an HMAC
  signature. The `sessions` table stores only a SHA-256 hash of the token.
- Discord access and refresh tokens are encrypted with AES-256-GCM, using a
  key derived from `SESSION_SECRET`, before they're stored.
- Username, display name, avatar and email are refreshed from Discord on every
  login. A first login creates the user, TV list, movie list and session in
  one transaction.
- `SameSite=Lax` keeps the session cookie off cross-site POSTs, which covers
  CSRF for `/auth/logout` and future write endpoints. Browsers accept `Secure`
  cookies on `http://localhost`, so local dev works without TLS.

### Build

```bash
CGO_ENABLED=0 go build -trimpath -o bin/server ./cmd/server
```

This produces a single static binary with no C toolchain needed. It logs JSON
to stdout. On SIGINT/SIGTERM it stops accepting requests, finishes in-flight
ones (up to 15s), then closes the DB.

## Tests

```bash
cd backend
go test ./testing/...
```

Each test gets its own temporary SQLite database and a mock Discord API
(`httptest.Server`), so the tests never contact Discord. They cover the OAuth
flow and state/CSRF checks, user and list creation, repeat logins, session
rejection (missing, tampered, unknown, expired), logout, `/api/me`, SQLite
pragmas on every pooled connection, foreign keys, cascades and config
validation.

## Backups (Litestream → Backblaze B2)

`litestream.yml` replicates `$DATA_DIR/beantrack.db` to `$B2_BUCKET` under the
`beantrack/` prefix. It targets **Litestream v0.5.18**.

Run the app as a child of Litestream:

```bash
litestream replicate -config litestream.yml -exec "./bin/server"
```

The app opens SQLite in WAL mode (required by Litestream) with
`busy_timeout=5000` and `foreign_keys=ON` on every connection. It never runs
`wal_checkpoint` itself: Litestream manages checkpoints, and SQLite's default
auto-checkpoint is left on.

In B2, set the bucket's lifecycle rule to "Keep only the last version of the
file". Litestream's files are immutable.

### Encryption

Litestream v0.5 removed the client-side `age` encryption that v0.3 had. A
v0.5 config with `age` identities or recipients now fails at startup. This
setup uses **SSE-C** instead (S3 server-side encryption with a
customer-provided key):

- `LITESTREAM_ENCRYPTION_KEY` is a base64-encoded 256-bit key. Litestream
  sends it with every upload and download. B2 encrypts the objects at rest
  with AES-256 and keeps only a hash of the key, not the key itself.
- **If you lose the key, the backups can't be decrypted. B2 can't recover
  them.** Store it in a password manager, separately from the server.
- Trade-off: B2 briefly handles plaintext (over TLS) while it encrypts. If
  you need client-side encryption, where B2 never sees plaintext, you'd have
  to pin Litestream v0.3.x and use its `age` config. Litestream v0.5 can't
  restore those replicas.
- Objects encrypted with SSE-C can't be downloaded from the B2 web UI. Use
  `litestream restore`.

### Restore

The restore uses the same environment variables, including the encryption
key.

1. Stop the app (and Litestream).
2. Restore to a new file:

   ```bash
   litestream restore -config litestream.yml \
     -o "$DATA_DIR/beantrack.restored.db" "$DATA_DIR/beantrack.db"
   ```

   Add `-timestamp 2026-11-01T12:00:00Z` for a point-in-time restore. Restore
   refuses to overwrite an existing file unless you pass `-force`.
3. Replace the live database:

   ```bash
   cd "$DATA_DIR"
   mv beantrack.db beantrack.db.bak
   rm -f beantrack.db-wal beantrack.db-shm
   mv beantrack.restored.db beantrack.db
   ```

4. Start the app under `litestream replicate` again.

On a fresh machine or an empty volume, run this before starting:

```bash
litestream restore -config litestream.yml -if-db-not-exists -if-replica-exists "$DATA_DIR/beantrack.db"
```

It does nothing if the DB already exists or no backup exists yet, so it's
safe as a container entrypoint step.

## Containerizing later

No Dockerfile yet, but the app is ready for one. It builds with
`CGO_ENABLED=0`, takes all config from env vars, listens on `0.0.0.0:$PORT`,
logs to stdout, shuts down gracefully, and exposes `GET /healthz`. Mount
`DATA_DIR` as a volume. Use the restore-if-missing command above, then
`litestream replicate -exec`, as the entrypoint.
