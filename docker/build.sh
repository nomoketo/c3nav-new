#!/usr/bin/env bash
set -e

PROJDIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$PROJDIR"
COMMIT="$(git rev-parse HEAD)"
CONTEXT="."

if [[ "$1" == "git" ]]; then
    git fetch origin
    COMMIT="$(git rev-parse origin/main)"
    CONTEXT="https://github.com/c3nav/c3nav.git#${COMMIT}"
fi

docker buildx build -f docker/Dockerfile \
    --platform linux/arm64,linux/amd64 \
    --label "org.opencontainers.image.version=${COMMIT}" \
    -t "ghcr.io/c3nav/c3nav:${COMMIT}" \
    --annotation org.opencontainers.image.source="https://github.com/c3nav/c3nav" \
    --annotation org.opencontainers.image.url="https://c3nav.de" \
    --annotation org.opencontainers.image.authors="c3nav team" \
    --annotation org.opencontainers.image.description="Indoor navigation for the Chaos Communication Congress and other events. - Core" \
    --cache-from "type=registry,ref=ghcr.io/c3nav/c3nav_cache:main" \
    --cache-to "type=registry,ref=ghcr.io/c3nav/c3nav_cache:main,mode=max" \
    --push "${CONTEXT}"

docker buildx build -f docker/tileserver.dockerfile \
    --platform linux/arm64,linux/amd64 \
    --label "org.opencontainers.image.version=${COMMIT}" \
    -t "ghcr.io/c3nav/c3nav-tileserver:${COMMIT}" \
    --annotation org.opencontainers.image.source="https://github.com/c3nav/c3nav" \
    --annotation org.opencontainers.image.url="https://c3nav.de" \
    --annotation org.opencontainers.image.authors="c3nav team" \
    --annotation org.opencontainers.image.description="Indoor navigation for the Chaos Communication Congress and other events. - Tileserver" \
    --cache-from "type=registry,ref=ghcr.io/c3nav/c3nav_cache:tileserver_main" \
    --cache-to "type=registry,ref=ghcr.io/c3nav/c3nav_cache:tileserver_main,mode=max" \
    --push "${CONTEXT}"
