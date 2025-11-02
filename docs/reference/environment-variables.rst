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

See Also
--------

- :doc:`exceptions` - Exception types raised when environment variables are missing or invalid
- :doc:`api/base` - The ``call_api`` function that uses these variables
