#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running Django management commands..."

# Use 'python' to let Vercel use the correct virtual environment
# where packages from requirements.txt have been installed.
python manage.py collectstatic --no-input --clear
python manage.py migrate