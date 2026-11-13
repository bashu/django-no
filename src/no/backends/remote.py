import json
import time
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request
from urllib.request import urlopen

from django.core.exceptions import ImproperlyConfigured

from .base import BaseBackend
from .local import LocalBackend

# Cloudflare blocks urllib's default "Python-urllib/3.x" with a 403.
HEADERS = {
    "User-Agent": "django-no (+https://github.com/bashu/django-no)",
    "Accept": "application/json",
}


class RemoteBackend(BaseBackend):
    _retry_after = 0.0

    def __init__(
        self,
        url: str = "https://naas.isalman.dev/no",
        timeout: float = 3,
        cooldown: float = 60,
        **options: Any,
    ) -> None:
        super().__init__(**options)
        if urlsplit(url).scheme not in ("http", "https"):
            msg = f"RemoteBackend url must be http(s), got {url!r}"
            raise ImproperlyConfigured(msg)
        self.url, self.timeout, self.cooldown = url, timeout, cooldown
        self.fallback = LocalBackend(**options)

    def get_reason(self) -> str:
        if time.monotonic() < self._retry_after:
            return self.fallback.get_reason()
        request = Request(self.url, headers=HEADERS)  # noqa: S310 (scheme validated in __init__)
        try:
            with urlopen(request, timeout=self.timeout) as r:  # noqa: S310 (scheme validated in __init__)
                return json.load(r)["reason"]
        except Exception:  # noqa: BLE001
            type(self)._retry_after = time.monotonic() + self.cooldown  # noqa: SLF001
            return self.fallback.get_reason()
