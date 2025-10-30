#!/bin/bash
set -e

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations and collect static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput
