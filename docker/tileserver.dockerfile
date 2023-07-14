# syntax=docker/dockerfile:1.4
FROM ubuntu:lunar as base
ENV DEBIAN_FRONTEND noninteractive

RUN --mount=type=cache,target=/var/cache/apt --mount=type=tmpfs,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y --no-install-recommends \
    python3.11=3.11.2-6ubuntu0.1 \
    libpython3.11=3.11.2-6ubuntu0.1 \
    python3.11-venv=3.11.2-6ubuntu0.1 \
    python3-pip=23.0.1+dfsg-1 \
    curl=7.88.1-8ubuntu2 \
    libpcre3=2:8.39-15 \
    tzdata=2023c-2exp1ubuntu1.1 \
    ca-certificates=20230311ubuntu0.23.04.1


FROM base as builder
RUN --mount=type=cache,target=/var/cache/apt --mount=type=tmpfs,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9ubuntu3 \
    python3.11-dev=3.11.2-6ubuntu0.1 \
    libpcre3-dev=2:8.39-15


COPY --link /src /app
WORKDIR /app

RUN --mount=type=cache,target=/pip-cache \
    python3.11 -m venv env && \
    . /app/env/bin/activate && \
    pip install --cache-dir /pip-cache --upgrade pip wheel && \
    pip install --cache-dir /pip-cache -r requirements-tileserver.txt && \
    pip install --cache-dir /pip-cache uwsgi

FROM base as final
RUN groupadd -r -g 500 c3nav && useradd -r -u 500 -g 500 -G www-data c3nav
RUN mkdir /data && chown -R c3nav:c3nav /data
VOLUME /data

COPY --link --chown=500:500 /src /app
COPY --from=builder --chown=500:500 /app/env /app/env

ENV C3NAV_DEBUG="" \
    C3NAV_LOGLEVEL="info" \
    C3NAV_DATA_DIR="/data" \
    C3NAV_RELOAD_INTERVAL="60" \
    UWSGI_WORKERS="8"

# The following environment variables need to be set to start the tileserver
# C3NAV_UPSTREAM_BASE
# C3NAV_TILE_SECRET or C3NAV_TILE_SECRET_FILE
# C3NAV_MEMCACHED_SERVER
#
# This are additional optional variables
# C3NAV_LOGFILE
# C3NAV_HTTP_AUTH

USER c3nav
WORKDIR /app
EXPOSE 8000 5000
HEALTHCHECK --start-period=10s --interval=10s --timeout=1s CMD curl -f http://localhost:8000/check || exit 1
CMD ["/app/env/bin/uwsgi", "--master", \
     "--wsgi", "c3nav.tileserver.wsgi", \
     "--pythonpath", "/app/src", \
     "--enable-threads", "--ignore-sigpipe", "--disable-logging", "--need-app", \
     "--stats", ":5000", \
     "--http", "0.0.0.0:8000"]