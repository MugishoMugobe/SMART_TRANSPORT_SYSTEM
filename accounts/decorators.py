from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

# The two roles that run day-to-day operations. PASSENGER is deliberately
# excluded — passengers browse and book, they don't manage the fleet.
STAFF_ROLES = ("STAFF", "ADMIN")


def user_role(user):
    return getattr(getattr(user, "profile", None), "role", None)


def is_staff_or_admin(user):
    """The single source of truth for "can this account manage the
    system" — used by both the Django views (via role_required below)
    and the REST API (api/permissions.py), so the two never drift apart."""
    return bool(user.is_authenticated) and (
        user.is_superuser or user_role(user) in STAFF_ROLES
    )


def role_required(*allowed_roles):
    """
    Restrict a view to users whose Profile.role is one of allowed_roles.
    Superusers always pass. Anyone else is bounced back with a flash
    message instead of a bare 403 — consistent with how the rest of the
    app surfaces errors via django.contrib.messages.

    Usage:
        @role_required("STAFF", "ADMIN")
        def vehicle_create(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("accounts:login")

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            role = getattr(getattr(user, "profile", None), "role", None)

            if role not in allowed_roles:
                messages.error(
                    request,
                    "You don't have permission to access that page."
                )
                return redirect("dashboard:home")

            return view_func(request, *args, **kwargs)

        return wrapped
    return decorator
