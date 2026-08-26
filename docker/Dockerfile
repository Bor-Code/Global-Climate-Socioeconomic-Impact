# =============================================================================
# Dockerfile — Analiz + dbt + Dagster webserver için tek image
# Multi-stage build: builder (bağımlılıklar) + runtime (minimal)
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder: uv ile bağımlılıkları derle
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# uv kurulumu (pip yerine — lock dosyası garantili kurulum)
COPY --from=ghcr.io/astral-sh/uv:0.4.0 /uv /usr/local/bin/uv

WORKDIR /app

# Önce sadece bağımlılık dosyalarını kopyala (layer cache optimizasyonu)
COPY pyproject.toml ./

# Sanal ortamı oluştur ve bağımlılıkları kur
RUN uv venv /opt/venv && \
    UV_PROJECT_ENVIRONMENT=/opt/venv uv pip install --no-cache -e ".[dev]"

# ---------------------------------------------------------------------------
# Stage 2 — Runtime: sadece çalışma ortamı
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Sistem bağımlılıkları (DuckDB için gerekli)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Builder'dan sanal ortamı kopyala
COPY --from=builder /opt/venv /opt/venv

# PATH'e sanal ortamı ekle
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Proje dosyalarını kopyala (ham veri hariç — volume mount edilecek)
COPY dbt_project/ ./dbt_project/
COPY analyses/ ./analyses/
COPY dashboard/ ./dashboard/
COPY orchestration/ ./orchestration/
COPY .env.example ./.env.example

# ---------------------------------------------------------------------------
# Default: Dagster webserver
# docker-compose.yml'de override edilebilir
# ---------------------------------------------------------------------------
EXPOSE 3000
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
