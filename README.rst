pythonanywhere-core
===================

Python SDK for PythonAnywhere API - programmatic management of PythonAnywhere
services including webapps, files, scheduled tasks, students, and websites.

Core library behind the `PythonAnywhere cli tool`_.

.. _PythonAnywhere cli tool: https://pypi.org/project/pythonanywhere/

Documentation
=============

Full documentation is available at https://core.pythonanywhere.com/

Development
===========

To create local development environment, run:

.. code-block:: shell

    uv sync --locked --extra test --extra docs

To run tests:

.. code-block:: shell

    uv run --locked --extra test pytest

To build docs:

.. code-block:: shell

    cd docs
    uv run --locked --extra docs sphinx-build -b html . _build

To build a source archive and wheel:

.. code-block:: shell

    uv build
