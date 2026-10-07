# syntax=docker/dockerfile:1
# Single service image for Cloud Run: backend only, no frontend, no supervisor.
# Built in the cloud by Cloud Build (`gcloud run deploy --source ./backend`).
FROM python:3.13-slim

# uv 0.12.23, pinned. The official image ships the static binary, so no
# `curl | sh` step and no extra package in the image.
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /usr/local/bin/

# Compile bytecode at build time. UV_PYTHON_DOWNLOADS=never: the base image's
# 3.13 already satisfies requires-python, so uv must not fetch an interpreter.
ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Non-root. `useradd` comes from the `passwd` package in the slim base.
RUN useradd --create-home --uid 10001 app

# Dependencies before source, so this layer is cached across app-code changes.
# psycopg[binary] ships manylinux aarch64/x86_64 wheels, so no compiler
# toolchain or libpq-dev is needed in the final image.
# --no-install-project: the app is imported from /app, not installed as a package.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts

ENV PATH="/app/.venv/bin:$PATH"

USER app

# Cloud Run supplies $PORT (8080 by default) and routes to it.
EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
