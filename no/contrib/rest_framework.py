from django.conf import settings

from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler

from no.backends.local import LocalBackend

STATUS_CODES = (status.HTTP_403_FORBIDDEN, status.HTTP_429_TOO_MANY_REQUESTS)


def get_local_reason():
    # Never hit a remote API here: 429s come in floods.
    options = getattr(settings, "NO", {}).get("OPTIONS", {})
    return LocalBackend(path=options.get("path")).get_reason()


def add_reason(response):
    """Add a "reason" to 403 and 429 JSON responses, for custom exception handlers."""
    if (
        response is not None
        and response.status_code in STATUS_CODES
        and isinstance(response.data, dict)
    ):
        response.data.setdefault("reason", get_local_reason())
    return response


def exception_handler(exc, context):
    return add_reason(drf_exception_handler(exc, context))
