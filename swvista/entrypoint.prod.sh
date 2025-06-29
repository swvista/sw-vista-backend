#!/bin/sh

echo " Running database migrations..."
python manage.py migrate --noinput

echo " Collecting static files..."
python manage.py collectstatic --noinput

echo " running server..."
python -m gunicorn --bind 0.0.0:8000 swvista.wsgi:application --workers 3 --timeout 120 --log-level info


echo "🚀 Starting Django..."
exec "$@"
