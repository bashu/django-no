import json

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

import pytest

from no.views import permission_denied
from no.views import too_many_requests


@pytest.fixture
def reasons_file(settings, tmp_path):
    path = tmp_path / "reasons.json"
    path.write_text(json.dumps(["Nope."]), encoding="utf-8")
    settings.NO = {"OPTIONS": {"path": str(path)}}
    return path


@pytest.fixture
def request_():
    return RequestFactory().get("/")


class TestPermissionDenied:
    def test_fallback_template(self, reasons_file, request_):
        response = permission_denied(request_, PermissionDenied())
        assert response.status_code == 403  # noqa: PLR2004
        assert b"<h1>403 Forbidden</h1>" in response.content
        assert b"<p>Nope.</p>" in response.content

    def test_custom_template(self, reasons_file, request_):
        response = permission_denied(
            request_,
            PermissionDenied("Staff only"),
            template_name="custom/403.html",
        )
        assert response.content == b"403|Nope.|Staff only\n"

    def test_handler403(self, reasons_file, client):
        response = client.get("/forbidden/")
        assert response.status_code == 403  # noqa: PLR2004
        assert b"<p>Nope.</p>" in response.content


class TestTooManyRequests:
    def test_fallback_template(self, reasons_file, request_):
        response = too_many_requests(request_)
        assert response.status_code == 429  # noqa: PLR2004
        assert b"<h1>429 Too Many Requests</h1>" in response.content
        assert b"<p>Nope.</p>" in response.content

    def test_custom_template(self, reasons_file, request_):
        response = too_many_requests(request_, template_name="custom/429.html")
        assert response.content == b"429|Nope.\n"
