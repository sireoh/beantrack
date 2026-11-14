# syntax=docker/dockerfile:1
# BeanTrack frontend: serves the pre-built SvelteKit static site (adapter-static, `build/`)
# with nginx, and reverse-proxies /api to the backend. Nothing is built here: run
# `npm run build` first (with PUBLIC_API_URL empty so the site calls the relative /api).
#
# Runtime settings (filled into the nginx config when the container starts):
#   BACKEND_URL           where /api is proxied to, e.g. http://backend:8000
#   NGINX_PORT            port nginx listens on inside the container
#   NGINX_MAX_BODY_SIZE   largest request body, e.g. for watchlist imports

ARG NGINX_VERSION=1.27-alpine
FROM nginxinc/nginx-unprivileged:${NGINX_VERSION}

LABEL org.opencontainers.image.source="https://github.com/sireoh/beantrack" \
      org.opencontainers.image.description="BeanTrack web app (static SvelteKit build served by nginx)" \
      org.opencontainers.image.licenses="UNLICENSED"

# Defaults only; docker-compose passes the real values from .env.
ENV NGINX_PORT=8080 \
    BACKEND_URL=http://backend:8000 \
    NGINX_MAX_BODY_SIZE=10m

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY build/ /usr/share/nginx/html/

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null "http://127.0.0.1:${NGINX_PORT}/" || exit 1
