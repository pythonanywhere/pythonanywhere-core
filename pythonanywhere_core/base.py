import os
import platform
from typing import Dict

import requests

from pythonanywhere_core import __version__
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
    "3.14": "python314",
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
    :raises NoTokenError: if API_TOKEN environment variable is not set

    Client identification can be provided via PYTHONANYWHERE_CLIENT environment
    variable (e.g., "pa/1.0.0" or "mcp-server/0.5.0") to help with usage analytics.
    """

    token = os.environ.get("API_TOKEN")
    if token is None:
        raise NoTokenError(helpful_token_error_message())

    base_user_agent = f"pythonanywhere-core/{__version__}"
    client_info = os.environ.get("PYTHONANYWHERE_CLIENT")

    if client_info:
        user_agent = f"{base_user_agent} ({client_info}; Python/{platform.python_version()})"
    else:
        user_agent = f"{base_user_agent} (Python/{platform.python_version()})"

    headers = {
        "Authorization": f"Token {token}",
        "User-Agent": user_agent
    }
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        **kwargs,
    )
    if response.status_code == 401:
        print(response, response.text)
        raise AuthenticationError(f"Authentication error {response.status_code} calling API: {response.text}")
    return response
