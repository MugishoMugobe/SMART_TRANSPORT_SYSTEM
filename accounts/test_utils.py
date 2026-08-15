"""
Shared test fixtures used across every app's test suite.

Not itself a TestCase — importing create_user() elsewhere keeps every
app's tests building users/roles the same way instead of duplicating the
"create a user, then set profile.role" dance six times over.
"""

import base64

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

DEFAULT_PASSWORD = "Str0ngPassw0rd!"

# A real (if tiny) 1x1 pixel GIF — ImageField runs the upload through
# Pillow, so garbage bytes fail validation; this is the smallest payload
# that actually decodes as an image.
_TINY_GIF = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)


def tiny_image_file(name="photo.gif"):
    return SimpleUploadedFile(name, _TINY_GIF, content_type="image/gif")


def create_user(username, role="PASSENGER", password=DEFAULT_PASSWORD, **extra):
    """Create a User with a Profile.role set. The Profile itself is
    auto-created by accounts.signals on User creation."""

    user = User.objects.create_user(username=username, password=password, **extra)
    user.profile.role = role
    user.profile.save(update_fields=["role"])
    return user


def create_staff(username="staff_user", **extra):
    return create_user(username, role="STAFF", **extra)


def create_admin(username="admin_user", **extra):
    return create_user(username, role="ADMIN", is_staff=True, is_superuser=True, **extra)


def create_passenger_user(username="passenger_user", **extra):
    return create_user(username, role="PASSENGER", **extra)
