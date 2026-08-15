"""
Role-based permission classes for the REST API.

Roles come from accounts.models.Profile.role (ADMIN / STAFF / PASSENGER),
the same field the HTML views and the login redirect already use — the
API enforces the exact same role model, not a parallel one.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.decorators import is_staff_or_admin


class IsStaffOrAdmin(BasePermission):
    """Only STAFF/ADMIN accounts may use this endpoint at all."""

    message = "This action is restricted to staff and administrators."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and is_staff_or_admin(request.user)
        )


class IsStaffAdminOrReadOnly(BasePermission):
    """Any authenticated user may read; only STAFF/ADMIN may write.

    Used for fleet-reference data (vehicles, routes, trips) that
    passengers need to browse in order to book, but must not edit.
    """

    message = "Only staff and administrators can create, edit or delete this resource."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_staff_or_admin(request.user)


class BookingAccessPermission(BasePermission):
    """
    STAFF/ADMIN: full access to every booking.
    PASSENGER: may create bookings, and may only read/update/cancel a
    booking that belongs to a passenger record sharing their account
    email. The queryset is additionally scoped in the view so a
    passenger's list endpoint never returns other riders' bookings.
    """

    message = "You can only manage your own bookings."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_staff_or_admin(request.user):
            return True
        return (
            bool(request.user.email)
            and obj.passenger.email.lower() == request.user.email.lower()
        )
