#!/bin/bash
set -e

echo "🚀 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🧩 Running Django migrations..."
python manage.py migrate --noinput || true

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed!"
