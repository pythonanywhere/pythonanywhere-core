Python Versions
===============

The ``pythonanywhere-core`` library provides a mapping between Python version strings and PythonAnywhere's internal Python version identifiers.

PYTHON_VERSIONS Mapping
------------------------

The ``PYTHON_VERSIONS`` dictionary in :mod:`pythonanywhere_core.base` maps user-friendly version strings to API identifiers:

.. code-block:: python

    from pythonanywhere_core.base import PYTHON_VERSIONS

    print(PYTHON_VERSIONS)
    # {
    #     "3.6": "python36",
    #     "3.7": "python37",
    #     "3.8": "python38",
    #     "3.9": "python39",
    #     "3.10": "python310",
    #     "3.11": "python311",
    #     "3.12": "python312",
    #     "3.13": "python313",
    #     "3.14": "python314",
    # }

Supported Versions
------------------

Currently Supported
~~~~~~~~~~~~~~~~~~~

The following Python versions are actively supported by PythonAnywhere:

- **Python 3.10** - ``"3.10"`` → ``"python310"``
- **Python 3.11** - ``"3.11"`` → ``"python311"``
- **Python 3.12** - ``"3.12"`` → ``"python312"``
- **Python 3.13** - ``"3.13"`` → ``"python313"``

Legacy Versions
~~~~~~~~~~~~~~~

These older versions are included in the mapping for backward compatibility:

- **Python 3.6** - ``"3.6"`` → ``"python36"`` (deprecated)
- **Python 3.7** - ``"3.7"`` → ``"python37"`` (deprecated)
- **Python 3.8** - ``"3.8"`` → ``"python38"`` (deprecated)
- **Python 3.9** - ``"3.9"`` → ``"python39"`` (deprecated)

Future Versions
~~~~~~~~~~~~~~~

- **Python 3.14** - ``"3.14"`` → ``"python314"`` (pre-release)

.. note::
   Check the `PythonAnywhere website <https://help.pythonanywhere.com/pages/DebuggingImportError/>`_
   for the most up-to-date list of supported Python versions.

Usage
-----

When Creating Webapps
~~~~~~~~~~~~~~~~~~~~~

Use the user-friendly version string when creating webapps:

.. code-block:: python

    from pythonanywhere_core.webapp import Webapp
    from pathlib import Path

    webapp = Webapp("myuser.pythonanywhere.com")
    webapp.create(
        python_version="3.12",  # Use the simple version string
        virtualenv_path=Path("/home/myuser/.virtualenvs/myenv"),
        project_path=Path("/home/myuser/myproject"),
        nuke=False
    )

The library automatically converts ``"3.12"`` to ``"python312"`` for the API call.

Direct API Usage
~~~~~~~~~~~~~~~~

If you're working directly with the API endpoint, you can access the mapping:

.. code-block:: python

    from pythonanywhere_core.base import PYTHON_VERSIONS, call_api, get_api_endpoint

    username = "myuser"
    python_version = "3.11"

    # Convert version string to API format
    api_python_version = PYTHON_VERSIONS[python_version]

    url = get_api_endpoint(username=username, flavor="webapps")
    response = call_api(
        url,
        "post",
        data={
            "domain_name": f"{username}.pythonanywhere.com",
            "python_version": api_python_version  # "python311"
        }
    )

Validation
~~~~~~~~~~

Check if a version is supported:

.. code-block:: python

    from pythonanywhere_core.base import PYTHON_VERSIONS

    def is_supported_version(version: str) -> bool:
        """Check if a Python version is supported."""
        return version in PYTHON_VERSIONS

    if is_supported_version("3.12"):
        print("Python 3.12 is supported")
    else:
        print("Version not supported")

    # Get all supported versions
    supported = list(PYTHON_VERSIONS.keys())
    print(f"Supported versions: {supported}")

Version Format
--------------

Input Format
~~~~~~~~~~~~

When specifying Python versions, use the format ``"MAJOR.MINOR"``:

- ✅ Correct: ``"3.10"``, ``"3.11"``, ``"3.12"``
- ❌ Wrong: ``"310"``, ``"3.10.5"``, ``"python310"``

API Format
~~~~~~~~~~

The API expects the format ``"pythonMAJORMINOR"`` (no dot, no space):

- ``"python310"`` for Python 3.10
- ``"python311"`` for Python 3.11
- ``"python312"`` for Python 3.12

The ``PYTHON_VERSIONS`` mapping handles this conversion automatically.

Common Patterns
---------------

Get Latest Version
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.base import PYTHON_VERSIONS

    # Get the latest version (assuming they're in order)
    latest_version = max(PYTHON_VERSIONS.keys(), key=lambda v: tuple(map(int, v.split("."))))
    print(f"Latest version: {latest_version}")

Filter by Minimum Version
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.base import PYTHON_VERSIONS

    min_version = (3, 10)

    supported_versions = [
        v for v in PYTHON_VERSIONS.keys()
        if tuple(map(int, v.split("."))) >= min_version
    ]
    print(f"Versions >= 3.10: {supported_versions}")

See Also
--------

- :doc:`api/webapp` - Webapp class that uses Python version mapping
- :doc:`api/base` - Base module containing PYTHON_VERSIONS constant
