"""
A single, predictable error envelope for the whole API.

Without this, DRF's default handler returns a different JSON shape for
validation errors ({"field": ["msg"]}) than for permission/auth errors
({"detail": "msg"}), which makes error handling on any client painful.
Every error below now comes back as:

    {"error": {"code": "...", "message": "...", "details": {...|null}}}
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler


def _envelope(code, message, details=None):
    return {"error": {"code": code, "message": message, "details": details}}


def api_exception_handler(exc, context):
    # Let plain Django ValidationErrors (raised from the services layer)
    # behave like DRF ValidationErrors instead of bubbling up as a 500.
    if isinstance(exc, DjangoValidationError):
        exc = drf_exceptions.ValidationError(detail=exc.messages)

    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()

    response = drf_default_handler(exc, context)

    if response is None:
        # Anything DRF doesn't recognise (a genuine bug) — still return a
        # well-formed 500 instead of leaking a stack trace to the client.
        return Response(
            _envelope("server_error", "An unexpected error occurred."),
            status=500,
        )

    if isinstance(exc, drf_exceptions.ValidationError):
        code = "validation_error"
        message = "One or more fields failed validation."
        details = response.data
    elif isinstance(exc, (drf_exceptions.NotAuthenticated, drf_exceptions.AuthenticationFailed)):
        code = "not_authenticated"
        message = "Authentication credentials were not provided or are invalid."
        details = None
    elif isinstance(exc, drf_exceptions.PermissionDenied):
        code = "permission_denied"
        message = str(exc.detail) if exc.detail else "You do not have permission to perform this action."
        details = None
    elif isinstance(exc, drf_exceptions.NotFound):
        code = "not_found"
        message = "The requested resource does not exist."
        details = None
    elif isinstance(exc, drf_exceptions.Throttled):
        code = "throttled"
        message = "Too many requests — please try again shortly."
        details = {"retry_after_seconds": exc.wait}
    else:
        code = "error"
        message = str(exc)
        details = response.data if isinstance(response.data, (dict, list)) else None

    response.data = _envelope(code, message, details)

    return response
