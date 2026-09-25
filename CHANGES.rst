Changes
-------

1.1.1 (2026-09-25)
~~~~~~~~~~~~~~~~~~

* Fix ``RemoteBackend`` always falling back to local reasons: send a
  ``User-Agent`` header, since Cloudflare blocks urllib's default with a 403
* Error pages and the REST framework handler now use the configured backend
  instead of always using local reasons
* Document ``RemoteBackend`` trade-offs and the default endpoint's rate limit

1.1.0 (2026-09-25)
~~~~~~~~~~~~~~~~~~

* Add ``no`` management command that prints a reason to say no
* Add Django REST framework exception handler that adds a ``reason`` to
  403 and 429 responses (``pip install django-no[drf]``)
* Add ``permission_denied`` (``handler403``) and ``too_many_requests`` error
  views with built-in fallback templates

1.0.0 (2026-09-25)
~~~~~~~~~~~~~~~~~~

* Initial release
