import getpass


from pythonanywhere_core.base import call_api, get_api_endpoint
from pythonanywhere_core.exceptions import DomainAlreadyExistsException, PythonAnywhereApiException


class Website:
    """ Interface for PythonAnywhere websites API.

    Uses ``pythonanywhere_core.base`` function ``get_api_endpoint`` to
    create url, which is stored in a class variable ``Website.api_endpoint``,
    then calls ``call_api`` with appropriate arguments to execute websites
    action.

    Methods:
        - :meth:`Website.create`: Create a new website.
        - :meth:`Website.get`: Retrieve information about a specific website.
        - :meth:`Website.list`: Get a list of all websites.
        - :meth:`Website.reload`: Reload the website.
        - :meth:`Website.auto_ssl`: Create and apply a Let's Encrypt SSL certificate.
        - :meth:`Website.get_ssl_info`: Get SSL certificate information.
        - :meth:`Website.delete`: Delete a website.
    """

    def __init__(self) -> None:
        self.websites_base_url = get_api_endpoint(username=getpass.getuser(), flavor="websites")
        self.domains_base_url = get_api_endpoint(username=getpass.getuser(), flavor="domains")


    def create(self, domain_name: str, command: str) -> dict:
        """Creates new website with ``domain_name`` and ``command``.

        :param domain_name: domain name for new website
        :param command: command for new website
        :returns: dictionary with created website info"""

        response = call_api(
            self.websites_base_url,
            "post",
            json={
                "domain_name": domain_name,
                "enabled": True,
                "webapp": {"command": command}
            }
        )
        if response.status_code == 400 and "domain with this domain name already exists" in response.text:
            raise DomainAlreadyExistsException

        if not response.ok:
            raise PythonAnywhereApiException(f"POST to create website failed with status code {response.status_code} and error message: {response.text}")

        return response.json()

    def get(self, domain_name: str) -> dict:
        """Returns dictionary with website info for ``domain_name``.
        :param domain_name:
        :return: dictionary with website info"""

        response = call_api(
            f"{self.websites_base_url}{domain_name}/",
            "get",
        )
        return response.json()

    def list(self) -> list:
        """Returns list of dictionaries with all websites info.
        :return: list of dictionaries with websites info"""

        response = call_api(
            self.websites_base_url,
            "get",
        )
        return response.json()

    def reload(self, domain_name: str) -> dict:
        """Reloads website with ``domain_name``.
        :param domain_name: domain name for website to reload
        :return: dictionary with response"""

        response = call_api(
            f"{self.websites_base_url}{domain_name}/reload/",
            "post",
        )
        return response.json()

    def auto_ssl(self, domain_name: str) -> dict:
        """Creates and applies a Let's Encrypt certificate for ``domain_name``.
        :param domain_name: domain name for website to apply the certificate to
        :return: dictionary with response"""
        response = call_api(
            f"{self.domains_base_url}{domain_name}/ssl/",
            "post",
            json={"cert_type": "letsencrypt-auto-renew"}
        )
        return response.json()

    def get_ssl_info(self, domain_name) -> dict:
        """Get SSL certificate info
        :param domain_name: domain name for website to get SSL info
        :return: dictionary with SSL certificate info"""
        url = f"{self.domains_base_url}{domain_name}/ssl/"
        response = call_api(url, "get")
        if not response.ok:
            raise PythonAnywhereApiException(f"GET SSL details via API failed, got {response}:{response.text}")

        return response.json()

    def delete(self, domain_name: str) -> dict:
        """Deletes website with ``domain_name``.
        :param domain_name: domain name for website to delete
        :return: empty dictionary"""

        call_api(
            f"{self.websites_base_url}{domain_name}/",
            "delete",
        )
        return {}
