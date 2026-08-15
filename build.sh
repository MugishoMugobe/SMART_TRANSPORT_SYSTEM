#!/usr/bin/env bash
# Render build step — installs dependencies, gathers static files, and
# applies migrations before the web process starts.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
