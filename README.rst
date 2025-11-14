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

    poetry install

To run tests:

.. code-block:: shell

    poetry run pytest

To build docs:

.. code-block:: shell

    cd docs
    poetry run sphinx-build -b html . _build
