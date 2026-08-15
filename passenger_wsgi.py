"""
Entry point cPanel's "Setup Python App" (Phusion Passenger) looks for.

cPanel creates a virtualenv and expects this exact filename at the
application's root directory, exposing a WSGI callable named
`application`. Django already builds one — this just re-exports it.

This file must live next to manage.py (the application root you set in
cPanel's Python App screen), which is this repo's root.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def _load_dotenv(path):
    """
    Minimal, dependency-free .env loader.

    cPanel's "Setup Python App" has an Environment Variables UI, but on
    at least one real deployment its saved values didn't actually
    persist to the running process — every DJANGO_* setting silently
    fell back to its (insecure, DEBUG=True) default with no visible
    error. This is a second, independent channel for the same
    variables: a plain KEY=VALUE file (see .env.example) sitting next
    to this one, which never gets committed (.env is in .gitignore).

    os.environ.setdefault() means a real environment variable — from
    cPanel's UI, or anywhere else — always wins if both are present;
    this only fills in what's otherwise missing.
    """
    if not os.path.exists(path):
        return

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]

            os.environ.setdefault(key, value)


_load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from STS.wsgi import application  # noqa: E402
