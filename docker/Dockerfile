FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.4.0 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv venv /opt/venv && \
    UV_PROJECT_ENVIRONMENT=/opt/venv uv pip install --no-cache -e ".[dev]"

FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY dbt_project/ ./dbt_project/
COPY analyses/ ./analyses/
COPY dashboard/ ./dashboard/
COPY orchestration/ ./orchestration/
COPY .env.example ./.env.example

EXPOSE 3000
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
