import getpass
from urllib.parse import urljoin

from pythonanywhere_core.base import call_api, get_api_endpoint


class Website:
    api_endpoint = get_api_endpoint(username=getpass.getuser(), flavor="websites")

    def create(self, domain_name: str, command: str):
        response = call_api(
            self.api_endpoint,
            "post",
            data={
                "domain_name": domain_name,
                "enabled": True,
                "webapp": {"command": command}
            }
        )
        return response.json()

    def get(self, domain_name: str):
        response = call_api(
            urljoin(self.api_endpoint, domain_name),
            "get",
        )
        return response.json()

    def list(self):
        raise NotImplemented

    def reload(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented
