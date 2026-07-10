FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* .
RUN uv sync --no-dev

COPY . .

ENV DBT_PROFILES_DIR=/app
WORKDIR /app/olist_analytics