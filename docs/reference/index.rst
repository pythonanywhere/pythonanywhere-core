Reference Documentation
=======================

Complete technical reference for the ``pythonanywhere-core`` API.

Quick Navigation
----------------

**Core Configuration:**
  - :doc:`environment-variables` - Required and optional environment variables
  - :doc:`python-versions` - Supported Python versions mapping
  - :doc:`exceptions` - Exception types and error handling

**API Modules:**
  - :doc:`api/base` - Core API communication functions
  - :doc:`api/webapp` - Web application management
  - :doc:`api/files` - File operations and sharing
  - :doc:`api/schedule` - Scheduled task management
  - :doc:`api/students` - Student account management
  - :doc:`api/website` - Website and domain management
  - :doc:`api/resources` - System resource information

Configuration & Core Concepts
------------------------------

.. toctree::
   :maxdepth: 2

   environment-variables
   python-versions
   exceptions

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api/index

Common Tasks
------------

Reloading a Webapp
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.webapp import Webapp

    webapp = Webapp("myuser.pythonanywhere.com")
    webapp.reload()

See :doc:`api/webapp` for complete webapp management API.

Uploading a File
~~~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.files import Files

    files = Files()

    with open("local_file.txt", "rb") as f:
        files.path_post("/home/myuser/remote_file.txt", f.read())

See :doc:`api/files` for complete file operations API.

Creating a Scheduled Task
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.schedule import Schedule

    schedule = Schedule(username="myuser")
    task = schedule.create(
        command="python /home/myuser/myscript.py",
        enabled=True,
        interval="daily",
        hour=3,
        minute=0
    )

See :doc:`api/schedule` for complete scheduled task API.

Sharing a File
~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.files import Files

    files = Files()
    status, url = files.sharing_post("/home/myuser/report.pdf")
    print(f"File {status}: {url}")

See :doc:`api/files` for file sharing API.

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

    from pythonanywhere_core.exceptions import (
        NoTokenError,
        AuthenticationError,
        PythonAnywhereApiException
    )

    try:
        webapp.reload()
    except NoTokenError:
        print("Set API_TOKEN environment variable")
    except AuthenticationError:
        print("Invalid API token")
    except PythonAnywhereApiException as e:
        print(f"API error: {e}")

See :doc:`exceptions` for complete exception reference.

Index and Search
----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
