import getpass

from pythonanywhere_core.base import call_api, get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException


class CPU:
    """Interface for PythonAnywhere CPU resources API.
    
    Uses `pythonanywhere_core.base` :method: `get_api_endpoint` to
    create url, which is stored in a class variable `CPU.base_url`,
    then calls `call_api` with appropriate arguments to execute CPU
    resource actions.

    Methods:
        - :meth:`CPU.get_cpu_usage`: Get current CPU usage information.
    """
    
    def __init__(self):
        self.base_url = get_api_endpoint(username=getpass.getuser(), flavor="cpu")

    def get_cpu_usage(self):
        """Get current CPU usage information.
        
        :returns: dictionary with CPU usage information including daily limit,
                 total usage, and next reset time
        :raises PythonAnywhereApiException: if API call fails
        """
        response = call_api(url=self.base_url, method="GET")
        if not response.ok:
            raise PythonAnywhereApiException(f"GET to {self.base_url} failed, got {response}:{response.text}")
        return response.json()