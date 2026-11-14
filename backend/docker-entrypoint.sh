#!/bin/sh
# Start BeanTrack's API inside the container:
#   1. (Litestream configured) restore the database from B2 if there is none yet
#   2. run database migrations
#   3. start uvicorn, wrapped in `litestream replicate` when Litestream is configured
#
# Litestream is optional: without the B2_* variables (or with LITESTREAM_ENABLED=false)
# the API simply starts on its own. Manual backups (/api/admin/backup) work either way.
set -eu

: "${DATA_DIR:=/app/data}"
: "${DATABASE_NAME:=beantrack.db}"
: "${BACKEND_PORT:=8000}"
: "${FORWARDED_ALLOW_IPS:=*}"
: "${LITESTREAM_ENABLED:=true}"
export DATA_DIR DATABASE_NAME

DB_PATH="$DATA_DIR/$DATABASE_NAME"
LITESTREAM_CONFIG=/app/litestream.yml
mkdir -p "$DATA_DIR"

use_litestream=false
if [ "$LITESTREAM_ENABLED" != "false" ] \
    && [ -n "${B2_KEY_ID:-}" ] && [ -n "${B2_APPLICATION_KEY:-}" ] \
    && [ -n "${B2_BUCKET_NAME:-}" ] && [ -n "${B2_ENDPOINT:-}" ]; then
    use_litestream=true
fi

if [ "$use_litestream" = true ]; then
    if [ ! -f "$DB_PATH" ]; then
        echo "entrypoint: no database at $DB_PATH, trying to restore it from the Litestream replica"
        litestream restore -config "$LITESTREAM_CONFIG" -if-replica-exists "$DB_PATH" \
            || echo "entrypoint: Litestream restore failed; starting with a new database"
    fi
else
    echo "entrypoint: Litestream disabled or B2 not configured; running without replication"
fi

echo "entrypoint: applying database migrations"
alembic upgrade head

set -- python -m uvicorn app.main:create_app --factory \
    --host 0.0.0.0 --port "$BACKEND_PORT" \
    --proxy-headers --forwarded-allow-ips "$FORWARDED_ALLOW_IPS"

if [ "$use_litestream" = true ]; then
    echo "entrypoint: starting the API under litestream replicate"
    exec litestream replicate -config "$LITESTREAM_CONFIG" -exec "$*"
fi
exec "$@"
