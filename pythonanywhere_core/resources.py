import getpass

from pythonanywhere_core.base import call_api, get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException


class CPU:
    def __init__(self):
        self.base_url = get_api_endpoint(username=getpass.getuser(), flavor="cpu")

    def get_cpu_usage(self):
        """Get current CPU usage information."""
        response = call_api(url=self.base_url, method="GET")
        if not response.ok:
            raise PythonAnywhereApiException(f"GET to {self.base_url} failed, got {response}:{response.text}")
        return response.json()