# ---------- 1. aşama: bağımlılıklar ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- 2. aşama: çalışma imajı ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=8080

# libpq-dev yerine yalnızca çalışma zamanı kütüphanesi
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=appuser:appuser . .

# Statik dosyalar (yalnızca admin + Swagger UI için) imaja gömülür
RUN SECRET_KEY=build-only DATABASE_URL=postgres://u:p@localhost:5432/db \
    python manage.py collectstatic --noinput

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/api/v1/health/" || exit 1

CMD ["sh", "-c", "gunicorn config.wsgi:application \
     --bind 0.0.0.0:${PORT} \
     --workers ${GUNICORN_WORKERS:-3} \
     --threads ${GUNICORN_THREADS:-2} \
     --timeout 30 \
     --graceful-timeout 20 \
     --access-logfile - --error-logfile - \
     --log-level info"]
