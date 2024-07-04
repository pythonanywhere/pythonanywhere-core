API wrapper for programmatic management of PythonAnywhere services.

It's a core code behind `PythonAnywhere cli tool`_.

.. _PythonAnywhere cli tool: https://pypi.org/project/pythonanywhere/


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
