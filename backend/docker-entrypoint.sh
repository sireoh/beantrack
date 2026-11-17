#!/bin/sh
# Start BeanTrack's API inside the container: run database migrations, then uvicorn.
# Backups to Backblaze B2 (daily + manual) are handled by the API itself.
set -eu

: "${DATA_DIR:=/app/data}"
: "${BACKEND_PORT:=8000}"
: "${FORWARDED_ALLOW_IPS:=127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}"
export DATA_DIR

mkdir -p "$DATA_DIR"

echo "entrypoint: applying database migrations"
alembic upgrade head

echo "entrypoint: starting the API on port $BACKEND_PORT"
exec python -m uvicorn app.main:create_app --factory \
    --host 0.0.0.0 --port "$BACKEND_PORT" \
    --proxy-headers --forwarded-allow-ips "$FORWARDED_ALLOW_IPS"
