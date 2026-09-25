import json

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

import pytest
from rest_framework import exceptions
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from no.contrib.rest_framework import exception_handler


@pytest.fixture
def reasons_file(settings, tmp_path):
    path = tmp_path / "reasons.json"
    path.write_text(json.dumps(["Nope."]), encoding="utf-8")
    settings.NO = {"OPTIONS": {"path": str(path)}}
    return path


def handle(exc):
    return exception_handler(exc, {})


class ForbiddenView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        raise exceptions.PermissionDenied


class TestExceptionHandler:
    def test_permission_denied(self, reasons_file):
        response = handle(exceptions.PermissionDenied())
        assert response.status_code == 403  # noqa: PLR2004
        assert response.data == {
            "detail": exceptions.PermissionDenied.default_detail,
            "reason": "Nope.",
        }

    def test_django_permission_denied(self, reasons_file):
        response = handle(DjangoPermissionDenied())
        assert response.status_code == 403  # noqa: PLR2004
        assert response.data["reason"] == "Nope."

    def test_throttled(self, reasons_file):
        response = handle(exceptions.Throttled(wait=60))
        assert response.status_code == 429  # noqa: PLR2004
        assert response.data["reason"] == "Nope."
        assert response["Retry-After"] == "60"

    @pytest.mark.parametrize(
        "exc",
        [exceptions.NotFound(), exceptions.ValidationError({"name": ["Required."]})],
    )
    def test_other_status_codes(self, reasons_file, exc):
        assert "reason" not in handle(exc).data

    def test_unhandled_exception(self):
        assert handle(ValueError()) is None

    def test_custom_backend(self, settings):
        settings.NO = {"BACKEND": "no.tests.backends.PoliteBackend"}
        response = handle(exceptions.PermissionDenied())
        assert response.data["reason"] == "No, thank you."

    def test_view(self, settings, reasons_file):
        settings.REST_FRAMEWORK = {
            "EXCEPTION_HANDLER": "no.contrib.rest_framework.exception_handler",
            "UNAUTHENTICATED_USER": None,
        }
        request = APIRequestFactory().get("/")
        response = ForbiddenView.as_view()(request)
        assert response.status_code == 403  # noqa: PLR2004
        assert response.data["reason"] == "Nope."
