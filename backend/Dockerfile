# syntax=docker/dockerfile:1
# BeanTrack API: FastAPI + SQLite, with Litestream for continuous B2 replication.
# All configuration comes from environment variables (see the root .env.example);
# nothing secret is baked into the image.

ARG PYTHON_VERSION=3.13
ARG LITESTREAM_VERSION=0.5.18

# --- Builder: install the app and its dependencies into a venv ---------------------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
COPY pyproject.toml ./
COPY app ./app
RUN pip install .

# --- Litestream binary (the image targets linux/amd64) ------------------------------
FROM python:${PYTHON_VERSION}-slim AS litestream
ARG LITESTREAM_VERSION
ADD https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-${LITESTREAM_VERSION}-linux-x86_64.tar.gz /tmp/litestream.tar.gz
RUN tar -xzf /tmp/litestream.tar.gz -C /usr/local/bin litestream \
    && /usr/local/bin/litestream version

# --- Runtime -----------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim

LABEL org.opencontainers.image.source="https://github.com/sireoh/beantrack" \
      org.opencontainers.image.description="BeanTrack API (FastAPI + SQLite + Litestream)" \
      org.opencontainers.image.licenses="UNLICENSED"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data

RUN groupadd --system --gid 10001 beantrack \
    && useradd --system --uid 10001 --gid beantrack --home-dir /app --shell /usr/sbin/nologin beantrack

COPY --from=builder /opt/venv /opt/venv
COPY --from=litestream /usr/local/bin/litestream /usr/local/bin/litestream

WORKDIR /app
COPY alembic.ini litestream.yml ./
COPY migrations ./migrations
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
# Strip Windows line endings in case the script was checked out with CRLF.
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p /app/data && chown -R beantrack:beantrack /app

USER beantrack
VOLUME ["/app/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"BACKEND_PORT\",\"8000\")}/api/health', timeout=4)"

ENTRYPOINT ["docker-entrypoint.sh"]
