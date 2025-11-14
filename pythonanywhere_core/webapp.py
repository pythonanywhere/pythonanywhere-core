from __future__ import annotations

import os
import getpass
from pathlib import Path
from textwrap import dedent
from typing import Any

from dateutil.parser import parse

from pythonanywhere_core.base import call_api, get_api_endpoint, PYTHON_VERSIONS
from pythonanywhere_core.exceptions import SanityException, PythonAnywhereApiException, MissingCNAMEException


class Webapp:
    """ Interface for PythonAnywhere webapps API.
    Uses `pythonanywhere_core.base` :method: `get_api_endpoint` to
    create url, which is stored in a class variable `Webapp.base_url`,
    then calls `call_api` with appropriate arguments to execute webapps
    action.

    Methods:
        - :meth:`Webapp.create`: Create a new webapp.
        - :meth:`Webapp.create_static_file_mapping`: Create a static file mapping.
        - :meth:`Webapp.add_default_static_files_mappings`: Add default static files mappings.
        - :meth:`Webapp.reload`: Reload the webapp.
        - :meth:`Webapp.set_ssl`: Set the SSL certificate and private key.
        - :meth:`Webapp.get_ssl_info`: Retrieve SSL certificate information.
        - :meth:`Webapp.delete_log`: Delete a log file.
        - :meth:`Webapp.get_log_info`: Retrieve log file information.
        - :meth:`Webapp.get`: Retrieve webapp information.
        - :meth:`Webapp.delete`: Delete webapp.
        - :meth:`Webapp.patch`: Patch webapp.

    Class Methods:
        - :meth:`Webapp.list_webapps`: List all webapps for the current user.
    """
    username = getpass.getuser()
    files_url = get_api_endpoint(username=username, flavor="files")
    webapps_url = get_api_endpoint(username=username, flavor="webapps")

    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.domain_url = f"{self.webapps_url}{self.domain}/"

    def __eq__(self, other: Webapp) -> bool:
        return self.domain == other.domain

    def sanity_checks(self, nuke: bool) -> None:
        """Check that we have a token, and that we don't already have a webapp for this domain.

        :param nuke: if True, skip the check for existing webapp

        :raises SanityException: if API token is missing or webapp already exists
        """
        token = os.environ.get("API_TOKEN")
        if not token:
            raise SanityException(
                dedent(
                    """
                Could not find your API token.
                You may need to create it on the Accounts page?
                You will also need to close this console and open a new one once you've done that.
                """
                )
            )

        if nuke:
            return

        response = call_api(self.domain_url, "get")
        if response.status_code == 200:
            raise SanityException(
                f"You already have a webapp for {self.domain}.\n\nUse the --nuke option if you want to replace it."
            )

    def create(self, python_version: str, virtualenv_path: Path, project_path: Path, nuke: bool) -> None:
        """Create a webapp for the given domain, using the given python version and virtualenv path

        :param python_version:  python version to use
        :param virtualenv_path: path to the virtualenv
        :param project_path: path to the project
        :param nuke: if True, delete any existing webapp for this domain

        :raises PythonAnywhereApiException: if API call fails
        """
        if nuke:
            call_api(self.domain_url, "delete")
        response = call_api(
            self.webapps_url,
            "post",
            data={"domain_name": self.domain, "python_version": PYTHON_VERSIONS[python_version]},
        )
        if not response.ok or response.json().get("status") == "ERROR":
            raise PythonAnywhereApiException(f"POST to create webapp via API failed, got {response}:{response.text}")
        response = call_api(
            self.domain_url, "patch", data={"virtualenv_path": virtualenv_path, "source_directory": project_path}
        )
        if not response.ok:
            raise PythonAnywhereApiException(
                "PATCH to set virtualenv path and source directory via API failed," f"got {response}:{response.text}"
            )

    def create_static_file_mapping(self, url_path: str, directory_path: Path) -> None:
        """Create a static file mapping via the API.

        :param url_path: URL path (e.g., '/static/')
        :param directory_path: Filesystem path to serve (as Path)

        :raises PythonAnywhereApiException: if API call fails
        """
        url = f"{self.domain_url}static_files/"
        call_api(url, "post", json=dict(url=url_path, path=str(directory_path)))

    def add_default_static_files_mappings(self, project_path: Path) -> None:
        """Add default static files mappings for /static/ and /media/.

        :param project_path: path to the project

        :raises PythonAnywhereApiException: if API call fails
        """
        self.create_static_file_mapping("/static/", Path(project_path) / "static")
        self.create_static_file_mapping("/media/", Path(project_path) / "media")

    def reload(self) -> None:
        """Reload webapp

        :raises MissingCNAMEException: if CNAME not found (reload succeeded)
        :raises PythonAnywhereApiException: if API call fails"""
        url = f"{self.domain_url}reload/"
        response = call_api(url, "post")
        if not response.ok:
            if response.status_code == 409 and response.json()["error"] == "cname_error":
                raise MissingCNAMEException()
            raise PythonAnywhereApiException(f"POST to reload webapp via API failed, got {response}:{response.text}")

    def set_ssl(self, certificate: str, private_key: str) -> None:
        """Set SSL certificate and private key for webapp.

        :param certificate: SSL certificate
        :param private_key: SSL private key

        :raises PythonAnywhereApiException: if API call fails
        """
        url = f"{self.domain_url}ssl/"
        response = call_api(url, "post", json={"cert": certificate, "private_key": private_key})
        if not response.ok:
            raise PythonAnywhereApiException(
                dedent(
                    f"""
                    POST to set SSL details via API failed, got {response}:{response.text}
                    If you just created an API token, you need to set the API_TOKEN environment variable or start a
                    new console.  Also you need to have setup a `{self.domain}` PythonAnywhere webapp for this to work.
                    """
                )
            )

    def get_ssl_info(self) -> dict[str, Any]:
        """Get SSL certificate info.

        :returns: dictionary with SSL certificate information including parsed expiration date

        :raises PythonAnywhereApiException: if API call fails
        """
        url = f"{self.domain_url}ssl/"
        response = call_api(url, "get")
        if not response.ok:
            raise PythonAnywhereApiException(f"GET SSL details via API failed, got {response}:{response.text}")

        result = response.json()
        result["not_after"] = parse(result["not_after"])
        return result

    def delete_log(self, log_type: str, index: int = 0) -> None:
        """Delete log file

        :param log_type: log type (access, error, server)
        :param index: log file index (0 for current, 1 for previous, etc.)

        :raises PythonAnywhereApiException: if API call fails
        """
        if index == 1:
            suffix = ".1"
        elif index > 1:
            suffix = f".{index}.gz"
        else:
            suffix = ""

        base_log_url = f"{self.files_url}path/var/log/{self.domain}.{log_type}.log"
        response = call_api(f"{base_log_url}{suffix}/", "delete")

        if not response.ok:
            raise PythonAnywhereApiException(f"DELETE log file via API failed, got {response}:{response.text}")

    def get_log_info(self) -> dict[str, list[int]]:
        """Get log files info.

        :returns: dictionary with log files info, keys are log types ('access', 'error', 'server'), 
                 values are lists of log file indices

        :raises PythonAnywhereApiException: if API call fails"""
        url = f"{self.files_url}tree/?path=/var/log/"
        response = call_api(url, "get")
        if not response.ok:
            raise PythonAnywhereApiException(f"GET log files info via API failed, got {response}:{response.text}")
        file_list = response.json()
        log_types = ["access", "error", "server"]
        logs = {"access": [], "error": [], "server": []}
        log_prefix = f"/var/log/{self.domain}."
        for file_name in file_list:
            if type(file_name) == str and file_name.startswith(log_prefix):
                log = file_name[len(log_prefix) :].split(".")
                if log[0] in log_types:
                    log_type = log[0]
                    if log[-1] == "log":
                        log_index = 0
                    elif log[-1] == "1":
                        log_index = 1
                    elif log[-1] == "gz":
                        log_index = int(log[-2])
                    else:
                        continue
                    logs[log_type].append(log_index)
        return logs

    @classmethod
    def list_webapps(cls) -> list[dict[str, Any]]:
        """List all webapps for the current user.

        :returns: list of webapps info as dictionaries

        :raises PythonAnywhereApiException: if API call fails
        """
        response = call_api(cls.webapps_url, "get")
        if not response.ok:
            raise PythonAnywhereApiException(
                f"GET webapps via API failed, "
                f"got {response}:{response.text}"
            )
        return response.json()

    def get(self) -> dict[str, Any]:
        """Retrieve webapp information.

        :returns: dictionary with webapp information

        :raises PythonAnywhereApiException: if API call fails
        """
        response = call_api(self.domain_url, "get")

        if not response.ok:
            raise PythonAnywhereApiException(
                f"GET webapp for {self.domain} via API failed, got {response}:{response.text}"
            )

        return response.json()

    def delete(self) -> None:
        """Delete webapp.

        :raises PythonAnywhereApiException: if API call fails
        """
        response = call_api(self.domain_url, "delete")

        if response.status_code != 204:
            raise PythonAnywhereApiException(
                f"DELETE webapp for {self.domain} via API failed, got {response}:{response.text}"
            )

    def patch(self, data: dict) -> dict[str, Any]:
        """Patch webapp with provided data.

        :param data: dictionary with data to update
        :returns: dictionary with updated webapp information

        :raises PythonAnywhereApiException: if API call fails
        """
        response = call_api(self.domain_url, "patch", data=data)

        if not response.ok:
            raise PythonAnywhereApiException(
                f"PATCH webapp for {self.domain} via API failed, "
                f"got {response}:{response.text}"
            )

        return response.json()
