Welcome to pythonanywhere-core
================================

API wrapper for programmatic management of PythonAnywhere services.

``pythonanywhere-core`` provides a Python interface for managing webapps, files, scheduled tasks,
students, and websites via the PythonAnywhere API. It serves as the core library behind the
`PythonAnywhere CLI tool`_ and `PythonAnywhere MCP server`_.

.. _PythonAnywhere CLI tool: https://pypi.org/project/pythonanywhere/
.. _PythonAnywhere MCP server: https://pypi.org/project/pythonanywhere-mcp-server/

Quick Start
-----------

Install the library:

.. code-block:: bash

    pip install pythonanywhere-core

Set up your API token (if running outside PythonAnywhere):

.. code-block:: bash

    export API_TOKEN="your_token_from_pythonanywhere_account_page"

.. note::
   **Creating your API token:** Go to the "Account" page on PythonAnywhere, then to the
   "API Token" tab, and click "Create a new API token".

   If you're running code on PythonAnywhere itself, the token is automatically available.
   You only need to set ``API_TOKEN`` when running locally or from external servers.

   See :doc:`reference/environment-variables` for more details on configuration.

Create your first webapp:

.. code-block:: python

    from pythonanywhere_core.webapp import Webapp
    from pathlib import Path

    webapp = Webapp("yourusername.pythonanywhere.com")
    webapp.create(
        python_version="3.12",
        virtualenv_path=Path("/home/yourusername/.virtualenvs/myenv"),
        project_path=Path("/home/yourusername/myproject"),
        nuke=False
    )
    webapp.reload()

Documentation
-------------

📖 **Reference Documentation**
   Complete technical specifications for all modules, classes, and functions.

   :doc:`Go to Reference → <reference/index>`

   - :doc:`reference/environment-variables` - Configuration via environment variables
   - :doc:`reference/python-versions` - Supported Python versions
   - :doc:`reference/exceptions` - Exception types and error handling
   - :doc:`API Reference <reference/api/index>` - Complete API reference

Installation
------------

Install via pip:

.. code-block:: bash

    pip install pythonanywhere-core

For development:

.. code-block:: bash

    git clone https://github.com/pythonanywhere/pythonanywhere-core.git
    cd pythonanywhere-core
    poetry install

See :doc:`installation` for more details.

Features
--------

- **Webapp Management**: Create, configure, reload, and delete WSGI web applications (Django, Flask, etc.)
- **Website Management**: Handle domains and website configuration for ASGI and other apps (FastAPI, Streamlit, etc.)
- **File Operations**: Upload, download, delete, and share files
- **SSL Configuration**: Set up and manage SSL certificates
- **Scheduled Tasks**: Create and manage scheduled tasks
- **Student Management**: Manage student accounts (for teachers)

Links
-----

- **GitHub Repository**: https://github.com/pythonanywhere/pythonanywhere-core
- **PyPI Package**: https://pypi.org/project/pythonanywhere-core/
- **PythonAnywhere API Docs**: https://help.pythonanywhere.com/pages/API/
- **Issue Tracker**: https://github.com/pythonanywhere/pythonanywhere-core/issues

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Documentation:

   installation
   reference/index

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
