#!/bin/sh
set -e

mkdir -p media
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# ASGI (uvicorn) serves both HTTP and the /ws/portal/ live-update socket.
if [ "${DJANGO_DEBUG:-0}" = "1" ]; then
  exec uvicorn vedelb2c.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --timeout-keep-alive 5
fi

exec uvicorn vedelb2c.asgi:application \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${UVICORN_WORKERS:-${GUNICORN_WORKERS:-2}}" \
  --proxy-headers \
  --forwarded-allow-ips '*' \
  --timeout-keep-alive 5
