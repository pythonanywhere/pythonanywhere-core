import getpass
from typing import Optional

from pythonanywhere_core.base import call_api, get_api_endpoint


class StudentsAPI:
    """
    Interface for the PythonAnywhere Students API.

    This class uses the `get_api_endpoint` function from
    ``pythonanywhere.api.base`` to construct the API URL, which is stored
    in the class variable ``base_url``. It then calls the ``call_api`` method
    with the appropriate arguments to perform student-related actions.

    Supported HTTP Methods:
        - `GET`
        - `DELETE`

    Methods:
        - :meth:`StudentsAPI.get`: Retrieve a list of students.
        - :meth:`StudentsAPI.delete`: Remove a student.
    """

    base_url: str = get_api_endpoint(username=getpass.getuser(), flavor="students")

    def get(self) -> Optional[dict]:
        """Returns list of PythonAnywhere students related with user's account.

        :returns: dictionary with students info
        """

        result = call_api(self.base_url, "GET")

        if result.status_code == 200:
            return result.json()

        raise Exception(f"GET to list students failed, got {result.text}")

    def delete(self, student_username: str) -> Optional[int]:
        """Returns 204 if student has been successfully removed, raises otherwise.

        :param student_username: student username to be removed
        :returns: 204 if student has been successfully removed
        """

        url = f"{self.base_url}{student_username}"

        result = call_api(url, "DELETE")

        if result.status_code == 204:
            return result.status_code

        detail = f": {result.text}" if result.text else ""
        raise Exception(
            f"DELETE to remove student {student_username!r} failed, got {result}{detail}"
        )
