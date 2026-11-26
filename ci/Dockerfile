# syntax=docker/dockerfile:1
#
# Two stages: uv installs the locked dependencies and the app into a virtualenv on Debian, then
# only that virtualenv is copied onto distroless Python (no shell, no package manager, non-root).
# Both stages are Debian 13, so the virtualenv's /usr/bin/python3 (3.13) exists in the runtime.
# Base images are pinned by digest; Dependabot (docker ecosystem) bumps them.

FROM ghcr.io/astral-sh/uv:0.13.10@sha256:a3ea1357342c1a4bf9a0c53a3deb1b55379aefa037338d8113d5771efa01774f AS uv

FROM debian:trixie-slim@sha256:8aa5a7bf5a1955bddbe7d74fcdd0b91ab30e74362a8b73af672b0481b35b44a0 AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=uv /uv /usr/local/bin/uv

# Use Debian's Python (the one distroless ships), compile bytecode once, and copy rather than
# hard-link so the virtualenv is self-contained.
ENV UV_PYTHON=/usr/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

WORKDIR /app

# Dependencies first, in their own layer, so a source-only change reuses it.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Then the app itself, installed non-editable so the runtime needs only the virtualenv.
COPY README.md gunicorn.conf.py ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

FROM gcr.io/distroless/python3-debian13:nonroot@sha256:72de1dda9d4c52c370e2ef2d93c28e3e1a8193c92058b7dfa42bace38a83d114

WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/gunicorn.conf.py /app/gunicorn.conf.py

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

EXPOSE 5000
USER nonroot

# gunicorn reads ./gunicorn.conf.py (bind from PORT, workers from WEB_CONCURRENCY).
ENTRYPOINT ["/app/.venv/bin/python", "-m", "gunicorn"]
