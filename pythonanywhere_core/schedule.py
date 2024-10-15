import getpass
from typing import List, Optional

from typing_extensions import Literal

from pythonanywhere_core.base import call_api, get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException


class Schedule:
    """
    Interface for the PythonAnywhere Scheduled Tasks API.

    This class uses the `get_api_endpoint` function from ``pythonanywhere_core.api``
    to construct the API URL, which is stored in the class variable ``base_url``.
    It then calls the ``call_api`` method with appropriate arguments to perform
    actions related to scheduled tasks.

    Supported HTTP Methods:
        - `GET` and `POST` for the tasks list.
        - `GET`, `PATCH`, and `DELETE` for tasks with an ID.

    Methods:
        - :meth:`Schedule.get_list`: Retrieve the list of all scheduled tasks.
        - :meth:`Schedule.create`: Create a new scheduled task.
        - :meth:`Schedule.get_specs`: Retrieve the specifications of an existing task.
        - :meth:`Schedule.delete`: Delete an existing task.
        - :meth:`Schedule.update`: Update an existing task.
    """

    base_url: str = get_api_endpoint(username=getpass.getuser(), flavor="schedule")

    def create(self, params: dict) -> Optional[dict]:
        """Creates new scheduled task using `params`.

        Params should be: command, enabled (True or False), interval (daily or
        hourly), hour (24h format) and minute.

        :param params: dictionary with required scheduled task specs
        :returns: dictionary with created task specs"""

        result = call_api(self.base_url, "POST", json=params)

        if result.status_code == 201:
            return result.json()

        if not result.ok:
            raise PythonAnywhereApiException(
                f"POST to set new task via API failed, got {result}: {result.text}"
            )

    def delete(self, task_id: int) -> Literal[True]:
        """Deletes scheduled task by id.

        :param task_id: scheduled task to be deleted id number
        :returns: True when API response is 204"""

        result = call_api(
            f"{self.base_url}{task_id}/", "DELETE"
        )

        if result.status_code == 204:
            return True

        if not result.ok:
            raise PythonAnywhereApiException(
                f"DELETE via API on task {task_id} failed, got {result}: {result.text}"
            )

    def get_list(self) -> List[dict]:
        """Gets list of existing scheduled tasks.

        :returns: list of existing scheduled tasks specs"""

        return call_api(self.base_url, "GET").json()

    def get_specs(self, task_id: int) -> dict:
        """Get task specs by id.

        :param task_id: existing task id
        :returns: dictionary of existing task specs"""

        result = call_api(
            f"{self.base_url}{task_id}/", "GET"
        )
        if result.status_code == 200:
            return result.json()
        else:
            raise PythonAnywhereApiException(
                f"Could not get task with id {task_id}. Got result {result}: {result.text}"
            )

    def update(self, task_id: int, params: dict) -> dict:
        """Updates existing task using id and params.

        Params should at least one of: command, enabled, interval, hour,
        minute. To update hourly task don't use 'hour' param. On the other
        hand when changing task's interval from 'hourly' to 'daily' hour is
        required.

        :param task_id: existing task id
        :param params: dictionary of specs to update"""

        result = call_api(
            f"{self.base_url}{task_id}/",
            "PATCH",
            json=params,
        )
        if result.status_code == 200:
            return result.json()
        else:
            raise PythonAnywhereApiException(
                f"Could not update task {task_id}. Got {result}: {result.text}"
            )
