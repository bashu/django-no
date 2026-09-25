Changes
-------

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
