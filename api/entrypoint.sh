#!/bin/sh
set -e

echo "→ Aplicando migraciones Alembic…"
alembic upgrade head

echo "→ Levantando Uvicorn en :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
