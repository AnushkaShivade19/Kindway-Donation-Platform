#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running Django management commands..."

# Vercel has already installed dependencies from requirements.txt
# We just need to run collectstatic and migrations.

python3.9 manage.py collectstatic --no-input --clear
python3.9 manage.py migrate