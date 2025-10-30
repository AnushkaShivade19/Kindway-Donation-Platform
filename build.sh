#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run Django management commands
python manage.py collectstatic --noinput
python manage.py migrate

# Launch server
gunicorn kindway.wsgi
