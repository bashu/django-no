from functools import cache

from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


@cache
def get_backend():
    conf = getattr(settings, "NO", {})
    backend = import_string(conf.get("BACKEND", "no.backends.local.LocalBackend"))
    return backend(**conf.get("OPTIONS", {}))


def get_reason():
    return get_backend().get_reason()


def handle_cache_clear(setting, **kwargs):
    if setting in ("NO",):
        get_backend.cache_clear()


setting_changed.connect(handle_cache_clear)
