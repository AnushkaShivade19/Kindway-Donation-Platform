#!/bin/bash
# Exit on error
set -o errexit

# The 'pip install' command will be in the Vercel UI
# The 'migrate' command must be run from your local machine

# All this file does is collect static files for S3/Vercel
python manage.py collectstatic --noinput