#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running Django management commands..."

# Vercel has already installed packages.
# We just use 'python' to run our commands.
python manage.py collectstatic --no-input --clear
python manage.py migrate

