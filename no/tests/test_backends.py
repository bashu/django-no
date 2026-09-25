import io
import json
from unittest import mock
from urllib.error import URLError

from django.core.exceptions import ImproperlyConfigured

import pytest

from no.backends import remote
from no.backends.base import BaseBackend
from no.backends.local import LocalBackend
from no.backends.local import from_path
from no.backends.remote import RemoteBackend


@pytest.fixture
def reasons_file(tmp_path):
    path = tmp_path / "reasons.json"
    path.write_text(json.dumps(["Nope."]), encoding="utf-8")
    return path


def response(payload):
    return io.BytesIO(json.dumps(payload).encode())


class TestBaseBackend:
    def test_options(self):
        assert BaseBackend(foo="bar").options == {"foo": "bar"}

    def test_get_reason(self):
        with pytest.raises(NotImplementedError):
            BaseBackend().get_reason()


class TestLocalBackend:
    def test_custom_path(self, reasons_file):
        assert from_path(str(reasons_file)) == ("Nope.",)

    def test_get_reason(self):
        assert LocalBackend().get_reason() in from_path()

    def test_get_reason_from_custom_path(self, reasons_file):
        assert LocalBackend(path=str(reasons_file)).get_reason() == "Nope."


class TestRemoteBackend:
    @pytest.mark.parametrize(
        "url",
        ["file:///etc/passwd", "ftp://example.com/no", "example.com/no"],
    )
    def test_broken_url(self, url):
        with pytest.raises(ImproperlyConfigured):
            RemoteBackend(url=url)

    def test_get_reason(self):
        backend = RemoteBackend(url="https://example.com/no", timeout=5)
        with mock.patch.object(
            remote,
            "urlopen",
            return_value=response({"reason": "Remote nope."}),
        ) as urlopen:
            assert backend.get_reason() == "Remote nope."
        urlopen.assert_called_once_with("https://example.com/no", timeout=5)

    @pytest.mark.parametrize(
        "side_effect",
        [
            URLError("unreachable"),
            TimeoutError(),
            lambda *args, **kwargs: io.BytesIO(b"not json"),
            lambda *args, **kwargs: response({"message": "no reason key"}),
            lambda *args, **kwargs: response(["not", "an", "object"]),
            RuntimeError("anything else"),
        ],
    )
    def test_fallback(self, reasons_file, side_effect):
        backend = RemoteBackend(path=str(reasons_file))
        with mock.patch.object(remote, "urlopen", side_effect=side_effect):
            assert backend.get_reason() == "Nope."
