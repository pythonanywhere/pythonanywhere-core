Environment Variables
=====================

The ``pythonanywhere-core`` library uses several environment variables for configuration.

Required Variables
------------------

API_TOKEN
~~~~~~~~~

**Required:** Yes

**Description:** Your PythonAnywhere API token used for authentication with the PythonAnywhere API.

**How to obtain:**
  1. Log into your PythonAnywhere account
  2. Go to the "Account" page
  3. Navigate to the "API Token" tab
  4. Click "Create a new API token"

**Usage:**

.. code-block:: bash

    export API_TOKEN="your_token_here"

**Exceptions:**
  - If not set, raises :class:`~pythonanywhere_core.exceptions.NoTokenError`
  - If invalid, API calls will raise :class:`~pythonanywhere_core.exceptions.AuthenticationError`

Optional Variables
------------------

PYTHONANYWHERE_SITE
~~~~~~~~~~~~~~~~~~~~

**Required:** No

**Default:** ``www.pythonanywhere.com`` (or ``www.`` + ``PYTHONANYWHERE_DOMAIN`` if that is set)

**Description:** Override the hostname used for API requests. Useful for testing against different PythonAnywhere environments or when using EU servers.

.. note::
   When running on PythonAnywhere, this variable is automatically set in the environment
   to match your system location (e.g., ``www.pythonanywhere.com`` or ``eu.pythonanywhere.com``).

**Usage:**

.. code-block:: bash

    export PYTHONANYWHERE_SITE="eu.pythonanywhere.com"

PYTHONANYWHERE_DOMAIN
~~~~~~~~~~~~~~~~~~~~~~

**Required:** No

**Default:** ``pythonanywhere.com``

**Description:** Override the domain used for constructing the API hostname. Used in combination with the site hostname. Only used when ``PYTHONANYWHERE_SITE`` is not set.

.. note::
   When running on PythonAnywhere, this variable is automatically set in the environment
   to match your domain (e.g., ``pythonanywhere.com``).

**Usage:**

.. code-block:: bash

    export PYTHONANYWHERE_DOMAIN="example.com"

PYTHONANYWHERE_CLIENT
~~~~~~~~~~~~~~~~~~~~~~

**Required:** No

**Default:** Not set (library identifies itself without client information)

**Description:** Identifies the client application using ``pythonanywhere-core`` in API requests. This information is included in the User-Agent header and helps PythonAnywhere understand API usage patterns and improve service analytics.

**Format:** ``client-name/version`` (e.g., ``pa/1.0.0``, ``mcp-server/0.5.0``)

**When to use:**
  - Building a CLI tool that uses this library
  - Creating an MCP server
  - Developing automation scripts or custom applications
  - Any downstream tool that wraps ``pythonanywhere-core``

**User-Agent format:**
  - Without ``PYTHONANYWHERE_CLIENT``: ``pythonanywhere-core/0.2.8 (Python/3.13.7)``
  - With ``PYTHONANYWHERE_CLIENT``: ``pythonanywhere-core/0.2.8 (pa/1.0.0; Python/3.13.7)``

**Usage:**

.. code-block:: python

    import os
    from importlib.metadata import version

    # Set at application startup
    CLI_VERSION = version("my-cli-package")
    os.environ["PYTHONANYWHERE_CLIENT"] = f"my-cli/{CLI_VERSION}"

See Also
--------

- :doc:`exceptions` - Exception types raised when environment variables are missing or invalid
- :doc:`api/base` - The ``call_api`` function that uses these variables
