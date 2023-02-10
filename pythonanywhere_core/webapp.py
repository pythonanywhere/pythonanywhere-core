from __future__ import annotations

import os
import getpass
from pathlib import Path
from textwrap import dedent

from dateutil.parser import parse
from snakesay import snakesay

from pythonanywhere_core.base import call_api, get_api_endpoint, PYTHON_VERSIONS
from pythonanywhere_core.exceptions import SanityException, PythonAnywhereApiException


class Webapp:
    def __init__(self, domain: str) -> None:
        self.endpoint = get_api_endpoint()
        self.username = getpass.getuser()
        self.files_url = self.endpoint.format(username=self.username, flavor="files")
        self.webapps_url = self.endpoint.format(username=self.username, flavor="webapps")
        self.domain = domain
        self.domain_url = f"{self.webapps_url}{self.domain}/"

    def __eq__(self, other: Webapp) -> bool:
        return self.domain == other.domain

    def sanity_checks(self, nuke: bool) -> None:
        print(snakesay("Running API sanity checks"))
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
        print(snakesay("Creating web app via API"))
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

    def add_default_static_files_mappings(self, project_path: Path) -> None:
        print(snakesay("Adding static files mappings for /static/ and /media/"))
        url = f"{self.domain_url}static_files/"
        call_api(url, "post", json=dict(url="/static/", path=str(Path(project_path) / "static")))
        call_api(url, "post", json=dict(url="/media/", path=str(Path(project_path) / "media")))

    def reload(self) -> None:
        print(snakesay(f"Reloading {self.domain} via API"))
        url = f"{self.domain_url}reload/"
        response = call_api(url, "post")
        if not response.ok:
            if response.status_code == 409 and response.json()["error"] == "cname_error":
                print(
                    snakesay(
                        dedent(
                            """
                            Could not find a CNAME for your website.  If you're using an A record,
                            CloudFlare, or some other way of pointing your domain at PythonAnywhere
                            then that should not be a problem.  If you're not, you should double-check
                            your DNS setup.
                        """
                        )
                    )
                )
                return
            raise PythonAnywhereApiException(f"POST to reload webapp via API failed, got {response}:{response.text}")

    def set_ssl(self, certificate: str, private_key: str) -> None:
        print(snakesay(f"Setting up SSL for {self.domain} via API"))
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
        url = f"{self.domain_url}ssl/"
        response = call_api(url, "get")
        if not response.ok:
            raise PythonAnywhereApiException(f"GET SSL details via API failed, got {response}:{response.text}")

        result = response.json()
        result["not_after"] = parse(result["not_after"])
        return result

    def delete_log(self, log_type: str, index: int = 0) -> None:
        if index:
            message = f"Deleting old (archive number {index}) {log_type} log file for {self.domain} via API"
        else:
            message = f"Deleting current {log_type} log file for {self.domain} via API"
        print(snakesay(message))

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

    def get_log_info(self):
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
