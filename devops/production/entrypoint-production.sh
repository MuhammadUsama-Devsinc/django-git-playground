#!/bin/sh

set -e

cd app
# Run migrations using absolute path to be safe
echo "Running migrations..."
python3 /app/manage.py migrate || echo "Migration failed"
echo "Migration is completed!"

# Collect static files
echo "Starting collectstatic..."
python3 /app/manage.py collectstatic --noinput
echo "Collectstatic is completed!"

echo "Starting server..."
exec gunicorn django_server.wsgi:application --bind 0.0.0.0:8000
