#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building project..."

# Install Python dependencies
pip install -r requirements.txt

# Run collectstatic
python manage.py collectstatic --no-input

# Run database migrations
# Note: It's often better to run migrations manually or in a separate process.
# This command is included for simplicity but can be risky in production.
python manage.py migrate