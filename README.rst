API wrapper for programmatic management of PythonAnywhere services.

It's a core code behind `PythonAnywhere cli tool`_.

.. _PythonAnywhere cli tool: https://pypi.org/project/pythonanywhere/

Documentation
=============

Full documentation is available at https://core.pythonanywhere.com/


Client Identification
=====================

If you're building a tool that uses ``pythonanywhere-core`` (e.g., CLI tool, MCP server, automation script), you can identify your client in API calls by setting the ``PYTHONANYWHERE_CLIENT`` environment variable:

.. code-block:: python

    import os
    os.environ["PYTHONANYWHERE_CLIENT"] = "my-tool/1.0.0"

    # Now all API calls will include your client identifier
    from pythonanywhere_core import Webapp
    webapp = Webapp("myuser")
    webapp.create(...)  # Automatically tagged

This helps PythonAnywhere understand API usage patterns and improves service analytics.

**Format:** ``client-name/version`` (e.g., ``cli/1.0.0``, ``mcp-server/0.5.0``)

The library automatically includes this information in the User-Agent header along with the library version and Python version.


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
