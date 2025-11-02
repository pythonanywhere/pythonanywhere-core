Exceptions
==========

The ``pythonanywhere-core`` library defines custom exception types for different error scenarios.

Exception Hierarchy
-------------------

.. code-block:: text

    Exception
    ├── AuthenticationError
    ├── SanityException
    └── PythonAnywhereApiException
        ├── NoTokenError
        └── DomainAlreadyExistsException

Exception Reference
-------------------

.. automodule:: exceptions
   :members:
   :show-inheritance:

Detailed Descriptions
---------------------

AuthenticationError
~~~~~~~~~~~~~~~~~~~

.. class:: AuthenticationError(Exception)
   :no-index:

   Raised when API authentication fails.

   **When raised:**
     - API returns a 401 Unauthorized status code
     - Invalid or expired API token

   **Common causes:**
     - Incorrect ``API_TOKEN`` environment variable
     - Expired API token
     - Token doesn't have required permissions

   **Example:**

   .. code-block:: python

       from pythonanywhere_core.base import call_api
       from pythonanywhere_core.exceptions import AuthenticationError
       import os

       os.environ["API_TOKEN"] = "invalid_token"

       try:
           call_api("https://www.pythonanywhere.com/api/v0/user/myuser/webapps/", "get")
       except AuthenticationError as e:
           print(f"Authentication failed: {e}")

   **Resolution:**
     - Verify your API token is correct
     - Generate a new token from the PythonAnywhere Account page
     - Ensure the token is properly set in the environment

SanityException
~~~~~~~~~~~~~~~

.. class:: SanityException(Exception)
   :no-index:

   Raised when pre-flight sanity checks fail.

   **When raised:**
     - Attempting to create a webapp that already exists (without ``nuke`` flag)
     - Missing API token during sanity checks
     - Invalid configuration detected before API operations

   **Common causes:**
     - Trying to create duplicate resources
     - Environment not properly configured

   **Example:**

   .. code-block:: python

       from pythonanywhere_core.webapp import Webapp
       from pythonanywhere_core.exceptions import SanityException

       webapp = Webapp("myuser.pythonanywhere.com")

       try:
           webapp.sanity_checks(nuke=False)
       except SanityException as e:
           print(f"Sanity check failed: {e}")
           # Use nuke=True to overwrite existing webapp

   **Resolution:**
     - Use the ``nuke`` parameter to overwrite existing resources
     - Ensure API token is properly configured
     - Check that resources don't already exist

PythonAnywhereApiException
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: PythonAnywhereApiException(Exception)
   :no-index:

   Base exception for all PythonAnywhere API-related errors.

   **When raised:**
     - Generic API operation failures
     - Unexpected API responses
     - Network or HTTP errors from the API

   **Common causes:**
     - API endpoint unreachable
     - Malformed API requests
     - Server-side errors

   **Example:**

   .. code-block:: python

       from pythonanywhere_core.webapp import Webapp
       from pythonanywhere_core.exceptions import PythonAnywhereApiException

       webapp = Webapp("myuser.pythonanywhere.com")

       try:
           webapp.reload()
       except PythonAnywhereApiException as e:
           print(f"API operation failed: {e}")

   **Resolution:**
     - Check the error message for specific details
     - Verify API endpoint URLs are correct
     - Ensure your account has required permissions

NoTokenError
~~~~~~~~~~~~

.. class:: NoTokenError(PythonAnywhereApiException)
   :no-index:

   Raised when the ``API_TOKEN`` environment variable is not set.

   **When raised:**
     - Any API call attempt without ``API_TOKEN`` environment variable

   **Common causes:**
     - Forgot to set environment variable
     - Running in a new shell session where variable wasn't exported
     - Environment variable was unset

   **Example:**

   .. code-block:: python

       import os
       from pythonanywhere_core.base import call_api
       from pythonanywhere_core.exceptions import NoTokenError

       # Unset token to demonstrate
       if "API_TOKEN" in os.environ:
           del os.environ["API_TOKEN"]

       try:
           call_api("https://www.pythonanywhere.com/api/v0/user/myuser/webapps/", "get")
       except NoTokenError as e:
           print(f"Token not found: {e}")

   **Resolution:**
     - Set the ``API_TOKEN`` environment variable:

       .. code-block:: bash

           export API_TOKEN="your_token_here"

     - See :doc:`environment-variables` for detailed setup instructions

DomainAlreadyExistsException
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: DomainAlreadyExistsException(PythonAnywhereApiException)
   :no-index:

   Raised when attempting to create a domain that already exists.

   **When raised:**
     - Creating a website/domain that is already registered

   **Common causes:**
     - Domain was previously created
     - Domain exists in your account

   **Resolution:**
     - Check existing domains before creating new ones
     - Delete the existing domain first if you want to recreate it
     - Use a different domain name

Best Practices
--------------

Exception Handling
~~~~~~~~~~~~~~~~~~

Always catch specific exceptions rather than generic ``Exception``:

.. code-block:: python

    from pythonanywhere_core.webapp import Webapp
    from pythonanywhere_core.exceptions import (
        NoTokenError,
        AuthenticationError,
        PythonAnywhereApiException
    )

    webapp = Webapp("myuser.pythonanywhere.com")

    try:
        webapp.reload()
    except NoTokenError:
        print("Please set your API_TOKEN environment variable")
    except AuthenticationError:
        print("Invalid API token - please generate a new one")
    except PythonAnywhereApiException as e:
        print(f"API error: {e}")

Graceful Degradation
~~~~~~~~~~~~~~~~~~~~

Handle errors gracefully in production code:

.. code-block:: python

    import sys
    from pythonanywhere_core.exceptions import SanityException

    webapp = Webapp("myuser.pythonanywhere.com")

    try:
        webapp.sanity_checks(nuke=False)
        webapp.create(python_version="3.10", virtualenv_path=venv, project_path=path, nuke=False)
    except SanityException as e:
        print(f"Error: {e}")
        print("Use --nuke flag to overwrite existing webapp")
        sys.exit(1)

See Also
--------

- :doc:`environment-variables` - Environment variable configuration
- :doc:`api/base` - Core API functions that raise these exceptions
