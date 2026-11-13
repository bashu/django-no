import io
import json
from collections.abc import Callable
from pathlib import Path
from unittest import mock
from urllib.error import URLError

from django.core.exceptions import ImproperlyConfigured

import pytest

from no.backends import remote
from no.backends.base import BaseBackend
from no.backends.local import LocalBackend
from no.backends.local import from_path
from no.backends.remote import RemoteBackend


def create_response(payload: object) -> io.BytesIO:
    return io.BytesIO(json.dumps(payload).encode())


class TestBaseBackend:
    def test_options(self) -> None:
        assert BaseBackend(foo="bar").options == {"foo": "bar"}

    def test_get_reason(self) -> None:
        with pytest.raises(NotImplementedError):
            BaseBackend().get_reason()


class TestLocalBackend:
    def test_custom_path(self, custom_reasons_file: Path) -> None:
        assert from_path(str(custom_reasons_file)) == ("Nope.",)

    def test_get_reason(self) -> None:
        assert LocalBackend().get_reason() in from_path()

    def test_get_reason_from_custom_path(self, custom_reasons_file: Path) -> None:
        assert LocalBackend(path=str(custom_reasons_file)).get_reason() == "Nope."


class TestRemoteBackend:
    @pytest.mark.parametrize(
        "url",
        ["file:///etc/passwd", "ftp://example.com/no", "example.com/no"],
    )
    def test_broken_url(self, url: str) -> None:
        with pytest.raises(
            ImproperlyConfigured,
            match=r"RemoteBackend url must be http\(s\)",
        ):
            RemoteBackend(url=url)

    def test_get_reason(self, monkeypatch: pytest.MonkeyPatch) -> None:
        urlopen = mock.Mock(return_value=create_response({"reason": "Remote nope."}))
        monkeypatch.setattr(remote, "urlopen", urlopen)
        backend = RemoteBackend(url="https://example.com/no", timeout=5)

        assert backend.get_reason() == "Remote nope."

        (request,), kwargs = urlopen.call_args
        assert request.full_url == "https://example.com/no"
        assert request.get_header("User-agent").startswith("django-no")
        assert request.get_header("Accept") == "application/json"
        assert kwargs == {"timeout": 5}

    @pytest.mark.parametrize(
        "side_effect",
        [
            URLError("unreachable"),
            TimeoutError(),
            lambda *args, **kwargs: io.BytesIO(b"not json"),
            lambda *args, **kwargs: create_response({"message": "no reason key"}),
            lambda *args, **kwargs: create_response(["not", "an", "object"]),
            RuntimeError("anything else"),
        ],
    )
    def test_fallback(
        self,
        monkeypatch: pytest.MonkeyPatch,
        custom_reasons_file: Path,
        side_effect: Exception | Callable[..., io.BytesIO],
    ) -> None:
        monkeypatch.setattr(remote, "urlopen", mock.Mock(side_effect=side_effect))
        # A failed request sets the cooldown on the class; restore it after the test.
        monkeypatch.setattr(RemoteBackend, "_retry_after", 0.0)
        backend = RemoteBackend(path=str(custom_reasons_file))

        assert backend.get_reason() == "Nope."
