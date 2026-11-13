from collections.abc import Callable
from typing import NoReturn

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

import pytest
from pytest_django import Settings
from rest_framework import exceptions
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from no.contrib.rest_framework import exception_handler


@pytest.fixture
def exception_response() -> Callable[[Exception], Response]:
    def handle_exception(exc: Exception) -> Response:
        response = exception_handler(exc, {})
        assert response is not None
        return response

    return handle_exception


class ForbiddenView(APIView):
    authentication_classes: list[type] = []
    permission_classes: list[type] = []

    def get(self, request: Request) -> NoReturn:
        raise exceptions.PermissionDenied


class TestExceptionHandler:
    @pytest.mark.usefixtures("custom_reasons_settings")
    def test_permission_denied(
        self,
        exception_response: Callable[[Exception], Response],
    ) -> None:
        response = exception_response(exceptions.PermissionDenied())

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": exceptions.PermissionDenied.default_detail,
            "reason": "Nope.",
        }

    @pytest.mark.usefixtures("custom_reasons_settings")
    def test_django_permission_denied(
        self,
        exception_response: Callable[[Exception], Response],
    ) -> None:
        response = exception_response(DjangoPermissionDenied())

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["reason"] == "Nope."

    @pytest.mark.usefixtures("custom_reasons_settings")
    def test_throttled(
        self,
        exception_response: Callable[[Exception], Response],
    ) -> None:
        response = exception_response(exceptions.Throttled(wait=60))

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.data["reason"] == "Nope."
        assert response["Retry-After"] == "60"

    @pytest.mark.usefixtures("custom_reasons_settings")
    @pytest.mark.parametrize(
        "exc",
        [exceptions.NotFound(), exceptions.ValidationError({"name": ["Required."]})],
    )
    def test_other_status_codes(
        self,
        exception_response: Callable[[Exception], Response],
        exc: exceptions.APIException,
    ) -> None:
        assert "reason" not in exception_response(exc).data

    def test_unhandled_exception(self) -> None:
        assert exception_handler(ValueError(), {}) is None

    def test_custom_backend(
        self,
        settings: Settings,
        exception_response: Callable[[Exception], Response],
    ) -> None:
        settings.NO = {"BACKEND": "tests.backends.PoliteBackend"}

        response = exception_response(exceptions.PermissionDenied())

        assert response.data["reason"] == "No, thank you."

    @pytest.mark.usefixtures("custom_reasons_settings")
    def test_view(self, settings: Settings) -> None:
        settings.REST_FRAMEWORK = {
            "EXCEPTION_HANDLER": "no.contrib.rest_framework.exception_handler",
            "UNAUTHENTICATED_USER": None,
        }
        request = APIRequestFactory().get("/")

        response = ForbiddenView.as_view()(request)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["reason"] == "Nope."
