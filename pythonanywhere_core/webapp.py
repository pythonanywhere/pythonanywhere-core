from __future__ import annotations

import os
import getpass
from pathlib import Path
from textwrap import dedent

from snakesay import snakesay

from pythonanywhere_core.base import call_api, get_api_endpoint, PYTHON_VERSIONS
from pythonanywhere_core.exceptions import SanityException, PythonAnywhereApiException


class Webapp:
    def __init__(self, domain: str) -> None:
        self.domain = domain

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

        endpoint = get_api_endpoint().format(username=getpass.getuser(), flavor="webapps")
        url = f"{endpoint}{self.domain}/"
        response = call_api(url, "get")
        if response.status_code == 200:
            raise SanityException(
                f"You already have a webapp for {self.domain}.\n\nUse the --nuke option if you want to replace it."
            )

    def create(self, python_version: str, virtualenv_path: Path, project_path: Path, nuke: bool) -> None:
        print(snakesay("Creating web app via API"))
        base_url = get_api_endpoint().format(username=getpass.getuser(), flavor="webapps")
        domain_url = f"{base_url}{self.domain}/"
        if nuke:
            call_api(domain_url, "delete")
        patch_url = domain_url
        response = call_api(
            base_url, "post", data={"domain_name": self.domain, "python_version": PYTHON_VERSIONS[python_version]}
        )
        if not response.ok or response.json().get("status") == "ERROR":
            raise PythonAnywhereApiException(
                f"POST to create webapp via API failed, got {response}:{response.text}"
            )
        response = call_api(
            patch_url, "patch", data={"virtualenv_path": virtualenv_path, "source_directory": project_path}
        )
        if not response.ok:
            raise PythonAnywhereApiException(
                "PATCH to set virtualenv path and source directory via API failed,"
                "got {response}:{response_text}".format(response=response, response_text=response.text)
            )
