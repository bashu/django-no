Example
=======

The example project uses `uv <https://docs.astral.sh/uv/>`_ and picks up
``no`` and its dependencies straight from the repository's
``pyproject.toml`` — no separate install step needed.

Run it
------

.. code-block:: bash

    uv run example/manage.py migrate
    uv run example/manage.py runserver

Then open http://127.0.0.1:8000/ for a reason to say no, rendered by the
``{% no %}`` template tag.

By default reasons come from the bundled list (``LocalBackend``). To fetch
them from the remote API instead, falling back to the bundled list whenever
it is unreachable:

.. code-block:: bash

    export NO_BACKEND="no.backends.remote.RemoteBackend"
    uv run example/manage.py runserver

Good luck!
