import os
from typing import Dict

import requests

from pythonanywhere_core.exceptions import AuthenticationError, NoTokenError

PYTHON_VERSIONS: Dict[str, str] = {
    "3.6": "python36",
    "3.7": "python37",
    "3.8": "python38",
    "3.9": "python39",
    "3.10": "python310",
    "3.11": "python311",
    "3.12": "python312",
    "3.13": "python313",
}


def get_api_endpoint(username: str, flavor: str) -> str:
    hostname = os.environ.get(
        "PYTHONANYWHERE_SITE",
        "www." + os.environ.get("PYTHONANYWHERE_DOMAIN", "pythonanywhere.com"),
    )
    if flavor == "websites" or flavor == "domains":
        return f"https://{hostname}/api/v1/user/{username}/{flavor}/"
    return f"https://{hostname}/api/v0/user/{username}/{flavor}/"


def helpful_token_error_message() -> str:
    if os.environ.get("PYTHONANYWHERE_SITE"):
        return (
            "Oops, you don't seem to have an API token.  "
            "Please go to the 'Account' page on PythonAnywhere, then to the 'API Token' "
            "tab.  Click the 'Create a new API token' button to create the token, then "
            "start a new console and try running me again."
        )
    else:
        return (
            "Oops, you don't seem to have an API_TOKEN environment variable set.  "
            "Please go to the 'Account' page on PythonAnywhere, then to the 'API Token' "
            "tab.  Click the 'Create a new API token' button to create the token, then "
            "use it to set API_TOKEN environmental variable and try running me again."
        )


def call_api(url: str, method: str, **kwargs) -> requests.Response:
    """Calls PythonAnywhere API with given url and method.

    :param url: url to call
    :param method: HTTP method to use
    :param kwargs: additional keyword arguments to pass to requests.request
    :returns: requests.Response object

    :raises AuthenticationError: if API returns 401
    :raises NoTokenError: if API_TOKEN environment variable is not set"""

    token = os.environ.get("API_TOKEN")
    if token is None:
        raise NoTokenError(helpful_token_error_message())
    insecure = os.environ.get("PYTHONANYWHERE_INSECURE_API") == "true"
    response = requests.request(
        method=method,
        url=url,
        headers={"Authorization": f"Token {token}"},
        verify=not insecure,
        **kwargs,
    )
    if response.status_code == 401:
        print(response, response.text)
        raise AuthenticationError(f"Authentication error {response.status_code} calling API: {response.text}")
    return response
