#!/bin/bash
set -o errexit

# pip install is in the UI
# migrate is done manually

# This is the only command that should be here
python manage.py collectstatic --noinput