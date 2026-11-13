from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from no import get_reason

STATUS_CODES = (status.HTTP_403_FORBIDDEN, status.HTTP_429_TOO_MANY_REQUESTS)


def add_reason(response: Response | None) -> Response | None:
    """Add a "reason" to 403 and 429 JSON responses, for custom exception handlers."""
    if (
        response is not None
        and response.status_code in STATUS_CODES
        and isinstance(response.data, dict)
    ):
        response.data.setdefault("reason", get_reason())
    return response


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    return add_reason(drf_exception_handler(exc, context))
