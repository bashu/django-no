from http import HTTPStatus

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import Client
from django.test import RequestFactory
from django.urls import reverse

import pytest
from pytest_django import Settings

from no.views import permission_denied
from no.views import too_many_requests


@pytest.fixture
def http_request() -> HttpRequest:
    return RequestFactory().get("/")


@pytest.fixture
def url_forbidden() -> str:
    return reverse("forbidden")


@pytest.mark.usefixtures("custom_reasons_settings")
class TestPermissionDenied:
    def test_fallback_template(self, http_request: HttpRequest) -> None:
        response = permission_denied(http_request, PermissionDenied())

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert b"<h1>403 Forbidden</h1>" in response.content
        assert b"<p>Nope.</p>" in response.content

    def test_custom_template(self, http_request: HttpRequest) -> None:
        response = permission_denied(
            http_request,
            PermissionDenied("Staff only"),
            template_name="custom/403.html",
        )

        assert response.content == b"403|Nope.|Staff only\n"

    def test_handler403(self, client: Client, url_forbidden: str) -> None:
        response = client.get(url_forbidden)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert b"<p>Nope.</p>" in response.content

    def test_custom_backend(
        self,
        settings: Settings,
        http_request: HttpRequest,
    ) -> None:
        settings.NO = {"BACKEND": "tests.backends.PoliteBackend"}

        response = permission_denied(http_request, PermissionDenied())

        assert b"<p>No, thank you.</p>" in response.content


@pytest.mark.usefixtures("custom_reasons_settings")
class TestTooManyRequests:
    def test_fallback_template(self, http_request: HttpRequest) -> None:
        response = too_many_requests(http_request)

        assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert b"<h1>429 Too Many Requests</h1>" in response.content
        assert b"<p>Nope.</p>" in response.content

    def test_custom_template(self, http_request: HttpRequest) -> None:
        response = too_many_requests(http_request, template_name="custom/429.html")

        assert response.content == b"429|Nope.\n"
