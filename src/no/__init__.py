from functools import cache
from typing import Any

from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

from .backends.base import BaseBackend


@cache
def get_backend() -> BaseBackend:
    conf = getattr(settings, "NO", {})
    backend = import_string(conf.get("BACKEND", "no.backends.local.LocalBackend"))
    return backend(**conf.get("OPTIONS", {}))


def get_reason() -> str:
    return get_backend().get_reason()


def handle_cache_clear(setting: str, **kwargs: Any) -> None:
    if setting in ("NO",):
        get_backend.cache_clear()


setting_changed.connect(handle_cache_clear)
