import getpass

from pythonanywhere_core.base import call_api, get_api_endpoint


class Website:
    """ Interface for PythonAnywhere websites API.

    Uses ``pythonanywhere_core.base`` :method: ``get_api_endpoint`` to
    create url, which is stored in a class variable ``Website.api_endpoint``,
    then calls ``call_api`` with appropriate arguments to execute websites
    action.

    Use :method: ``Website.create`` to create new website.
    Use :method: ``Website.get`` to get website info.
    Use :method: ``Website.list`` to get all websites list.
    Use :method: ``Website.reload`` to reload website.
    Use :method: ``Website.delete`` to delete website.
    """

    api_endpoint = get_api_endpoint(username=getpass.getuser(), flavor="websites")

    def create(self, domain_name: str, command: str) -> dict:
        """Creates new website with ``domain_name`` and ``command``.

        :param domain_name: domain name for new website
        :param command: command for new website
        :returns: dictionary with created website info"""

        response = call_api(
            self.api_endpoint,
            "post",
            json={
                "domain_name": domain_name,
                "enabled": True,
                "webapp": {"command": command}
            }
        )
        return response.json()

    def get(self, domain_name: str) -> dict:
        """Returns dictionary with website info for ``domain_name``.
        :param domain_name:
        :return: dictionary with website info"""

        response = call_api(
            f"{self.api_endpoint}{domain_name}/",
            "get",
        )
        return response.json()

    def list(self) -> list:
        """Returns list of dictionaries with all websites info.
        :return: list of dictionaries with websites info"""

        response = call_api(
            self.api_endpoint,
            "get",
        )
        return response.json()

    def reload(self, domain_name: str) -> dict:
        """Reloads website with ``domain_name``.
        :param domain_name: domain name for website to reload
        :return: dictionary with response"""

        response = call_api(
            f"{self.api_endpoint}{domain_name}/reload/",
            "post",
        )
        return response.json()

    def delete(self, domain_name: str) -> dict:
        """Deletes website with ``domain_name``.
        :param domain_name: domain name for website to delete
        :return: empty dictionary"""

        call_api(
            f"{self.api_endpoint}{domain_name}/",
            "delete",
        )
        return {}
