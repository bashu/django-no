django-no
================

.. image:: https://badge.fury.io/py/django-no.svg
    :target: https://badge.fury.io/py/django-no

.. image:: https://img.shields.io/pypi/pyversions/django-no.svg
    :target: https://pypi.python.org/pypi/django-no/

.. image:: https://img.shields.io/pypi/djversions/django-no.svg
    :target: https://pypi.python.org/pypi/django-no/

.. image:: https://github.com/bashu/django-no/actions/workflows/test.yml/badge.svg
    :target: https://github.com/bashu/django-no/actions/workflows/test.yml

Reusable django_ app that gives you a reason to say no. Reasons come from
a bundled list or from a remote
`No-as-a-Service (NaaS) <https://github.com/hotheadhacker/no-as-a-service>`_ API,
and can be rendered in templates or fetched from Python code.

Authored by `Basil Shubin <https://github.com/bashu/>`_, and some great
`contributors <https://github.com/bashu/django-no/contributors>`_.

Installation
------------

First install the module, preferably in a virtual environment. It can be installed from PyPI:

.. code-block:: shell

    pip install django-no

Requires Python 3.10+ and Django 5.2+.

Setup
-----

You'll need to add ``no`` to ``INSTALLED_APPS`` in your project's ``settings.py`` file:

.. code-block:: python

    INSTALLED_APPS += [
        "no",
    ]

There are no models, so no migrations are needed.

Usage
-----

Load the ``no`` template tag library and use the ``{% no %}`` tag:

.. code-block:: html+django

    {% load no %}

    <blockquote>{% no %}</blockquote>

Or store the reason in a variable:

.. code-block:: html+django

    {% load no %}

    {% no as reason %}
    <p title="{{ reason }}">No.</p>

Every ``{% no %}`` picks a new reason. Reasons are auto-escaped like any
other template output.

From Python code:

.. code-block:: python

    from no import get_reason

    get_reason()  # "I'm on a strict 'no commitments' diet."

Or from the command line:

.. code-block:: shell

    ./manage.py no

Error pages
~~~~~~~~~~~

Tell users *why* not on 403 pages, in your root URLconf:

.. code-block:: python

    handler403 = "no.views.permission_denied"

Django has no ``handler429``, so hand ``no.views.too_many_requests`` to your
rate limiter instead, e.g. `django-ratelimit
<https://github.com/jsocol/django-ratelimit>`_:

.. code-block:: python

    RATELIMIT_VIEW = "no.views.too_many_requests"

Both render your own ``403.html`` / ``429.html`` if you have one, with
``{{ reason }}`` and ``{{ exception }}`` in the context, and fall back to a
minimal built-in page otherwise. Reasons come from the configured backend;
if that's ``RemoteBackend``, read the notes under `RemoteBackend`_ first.

Django REST framework
~~~~~~~~~~~~~~~~~~~~~

Add a ``reason`` to every 403 and 429 JSON response:

.. code-block:: shell

    pip install django-no[drf]

.. code-block:: python

    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "no.contrib.rest_framework.exception_handler",
    }

.. code-block:: json

    {
        "detail": "You do not have permission to perform this action.",
        "reason": "I'm on a strict 'no commitments' diet."
    }

Reasons come from the configured backend, same as error pages above.
Already have a custom exception handler? Pass its response through
``no.contrib.rest_framework.add_reason()``.

Configuration
-------------

Everything is optional. Without any configuration reasons are picked at
random from the bundled list. To change that, set ``NO`` in your
``settings.py``:

.. code-block:: python

    NO = {
        "BACKEND": "no.backends.local.LocalBackend",
        "OPTIONS": {},
    }

``BACKEND`` is the dotted path to a backend class and ``OPTIONS`` is passed
to it as keyword arguments.

LocalBackend
~~~~~~~~~~~~

The default. Picks a random reason from a JSON file containing a list of
strings.

``path``
    Path to your own reasons file. Defaults to the bundled ``reasons.json``.

.. code-block:: python

    NO = {
        "BACKEND": "no.backends.local.LocalBackend",
        "OPTIONS": {"path": BASE_DIR / "reasons.json"},
    }

RemoteBackend
~~~~~~~~~~~~~

Fetches a reason from an HTTP API that responds with
``{"reason": "..."}``. Whenever the request fails it falls back to
``LocalBackend`` and stops calling the API for ``cooldown`` seconds.

``url``
    API endpoint, must be ``http`` or ``https``. Defaults to
    ``https://naas.isalman.dev/no``.
``timeout``
    Request timeout in seconds. Defaults to ``3``.
``cooldown``
    Seconds to wait before retrying the API after a failure. Defaults to ``60``.
``path``
    Reasons file for the fallback ``LocalBackend``.

.. code-block:: python

    NO = {
        "BACKEND": "no.backends.remote.RemoteBackend",
        "OPTIONS": {"timeout": 1, "cooldown": 300},
    }

Things to consider before using it:

* Every reason is an HTTP request made while the response is built, so a
  slow API slows down your pages by up to ``timeout`` seconds.
* The default public endpoint is rate limited to 120 requests per minute.
  Past that it answers 429, and ``RemoteBackend`` falls back to local reasons
  for ``cooldown`` seconds. Fine for a hobby site; for anything busier, run
  your own `no-as-a-service <https://github.com/hotheadhacker/no-as-a-service>`_
  instance and point ``url`` at it, or stick with ``LocalBackend``.
* Error responses tend to come in floods, 429s especially. With error pages
  or the REST framework handler enabled, every one of them is also a request
  to ``url``. Make sure your endpoint can take it.

Custom backends
~~~~~~~~~~~~~~~

Subclass ``no.backends.base.BaseBackend`` and implement ``get_reason()``.
``OPTIONS`` are available as ``self.options``:

.. code-block:: python

    from no.backends.base import BaseBackend

    class PoliteBackend(BaseBackend):
        def get_reason(self):
            return self.options.get("reason", "No, thank you.")

Example
-------

Please see the ``example`` application. This application is used to
manually test the functionalities of this package. This also serves as
a good example.

Contributing
------------

If you've found a bug, implemented a feature or have a good reason to say
no and think it is useful then please consider contributing. Patches, pull
requests or just suggestions are welcome!

License
-------

``django-no`` is released under the MIT license.

.. _django: https://www.djangoproject.com
