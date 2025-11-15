#!/bin/bash

# --- Build Script for Vercel ---

# 1. Install all Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 2. Collect all static files
# This gathers all static files (CSS, JS, images)
# into the 'staticfiles' directory specified in settings.py
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 3. Apply database migrations
# This runs 'migrate' on your Neon production database
echo "Applying database migrations..."
python manage.py migrate