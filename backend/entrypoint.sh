#!/bin/sh

echo "Starting entrypoint script..."
# Apply database migrations
python manage.py makemigrations
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input

# Start Daphne server
daphne -b 0.0.0.0 -p 8000 auth_site.asgi:application