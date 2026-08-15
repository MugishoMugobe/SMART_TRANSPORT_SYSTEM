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

from STS.wsgi import application  # noqa: E402
