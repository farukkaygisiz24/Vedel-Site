#!/bin/sh
set -e

mkdir -p media
python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${DJANGO_DEBUG:-0}" = "1" ]; then
  # Threads: a browser's idle preconnect would otherwise block the single sync worker.
  exec gunicorn vedelb2c.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --threads 8 \
    --reload \
    --timeout 60
fi

exec gunicorn vedelb2c.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-2}" \
  --threads "${GUNICORN_THREADS:-4}" \
  --timeout 60
