import getpass
from typing import Tuple, Union
from urllib.parse import urljoin

from requests.models import Response

from pythonanywhere_core.base import call_api, get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException


class Files:
    """
    Interface for the PythonAnywhere Files API.

    This class uses the `get_api_endpoint` function from ``pythonanywhere_core.base``
    to construct the API URL, which is stored in the class variable ``base_url``.
    It then calls the ``call_api`` method with the appropriate arguments to
    perform file-related actions.

    Supported Endpoints:
        - `GET`, `POST`, and `DELETE` for the files path endpoint.
        - `POST`, `GET`, and `DELETE` for the file sharing endpoint.
        - `GET` for the tree endpoint.

    Path Methods:
        - :meth:`Files.path_get`: Retrieve the contents of a file or directory from a specified `path`.
        - :meth:`Files.path_post`: Upload or update a file at the given `dest_path` using contents from `source`.
        - :meth:`Files.path_delete`: Delete a file or directory at the specified `path`.

    Sharing Methods:
        - :meth:`Files.sharing_post`: Enable sharing of a file from the given `path` (if not already shared) and get a link to it.
        - :meth:`Files.sharing_get`: Retrieve the sharing URL for a specified `path`.
        - :meth:`Files.sharing_delete`: Disable sharing for a specified `path`.

    Tree Method:
        - :meth:`Files.tree_get`: Retrieve a list of regular files and subdirectories of a directory at the specified `path`
          (limited to 1000 results).
    """


    base_url = get_api_endpoint(username=getpass.getuser(), flavor="files")
    path_endpoint = urljoin(base_url, "path")
    sharing_endpoint = urljoin(base_url, "sharing/")
    tree_endpoint = urljoin(base_url, "tree/")

    def _error_msg(self, result: Response)  -> str:
        """TODO: error responses should be unified at the API side """

        if "application/json" in result.headers.get("content-type", ""):
            jsn = result.json()
            msg = jsn.get("detail") or jsn.get("message") or jsn.get("error", "")
            return f": {msg}"
        return ""

    def _make_sharing_url(self, sharing_url_suffix):
        return urljoin(self.base_url.split("api")[0], sharing_url_suffix)

    def path_get(self, path: str) -> Union[dict, bytes]:
        """Returns dictionary of directory contents when `path` is an
        absolute path to of an existing directory or file contents if
        `path` is an absolute path to an existing file -- both
        available to the PythonAnywhere user.  Raises when `path` is
        invalid or unavailable."""

        url = f"{self.path_endpoint}{path}"

        result = call_api(url, "GET")

        if result.status_code == 200:
            if "application/json" in result.headers.get("content-type", ""):
                return result.json()
            return result.content

        raise PythonAnywhereApiException(
            f"GET to fetch contents of {url} failed, got {result}{self._error_msg(result)}"
        )

    def path_post(self, dest_path: str, content: bytes) -> int:
        """Uploads contents of `content` to `dest_path` which should be
        a valid absolute path of a file available to a PythonAnywhere
        user.  If `dest_path` contains directories which don't exist
        yet, they will be created.

        Returns 200 if existing file on PythonAnywhere has been
        updated with `source` contents, or 201 if file from
        `dest_path` has been created with those contents."""

        url = f"{self.path_endpoint}{dest_path}"

        result = call_api(url, "POST", files={"content": content})

        if result.ok:
            return result.status_code

        raise PythonAnywhereApiException(
            f"POST to upload contents to {url} failed, got {result}{self._error_msg(result)}"
        )

    def path_delete(self, path: str) -> int:
        """Deletes the file at specified `path` (if file is a
        directory it will be deleted as well).

        Returns 204 on sucess, raises otherwise."""

        url = f"{self.path_endpoint}{path}"

        result = call_api(url, "DELETE")

        if result.status_code == 204:
            return result.status_code

        raise PythonAnywhereApiException(
            f"DELETE on {url} failed, got {result}{self._error_msg(result)}"
        )

    def sharing_post(self, path: str) -> Tuple[str, str]:
        """Starts sharing a file at `path`.

        Returns a tuple with a message and sharing link on
        success, raises otherwise.  Message is "successfully shared" on success,
        "was already shared" if file has been already shared."""

        url = self.sharing_endpoint

        result = call_api(url, "POST", json={"path": path})

        if result.ok:
            msg = {200: "was already shared", 201: "successfully shared"}[result.status_code]
            sharing_url_suffix = result.json()["url"]
            return msg, self._make_sharing_url(sharing_url_suffix)

        raise PythonAnywhereApiException(
            f"POST to {url} to share '{path}' failed, got {result}{self._error_msg(result)}"
        )

    def sharing_get(self, path: str) -> str:
        """Checks sharing status for a `path`.

        Returns url with sharing link if file is shared or an empty
        string otherwise."""

        url = f"{self.sharing_endpoint}?path={path}"

        result = call_api(url, "GET")
        if result.ok:
            sharing_url_suffix = result.json()["url"]
            return self._make_sharing_url(sharing_url_suffix)
        else:
            return ""

    def sharing_delete(self, path: str) -> int:
        """Stops sharing file at `path`.

        Returns 204 on successful unshare."""

        url = f"{self.sharing_endpoint}?path={path}"

        result = call_api(url, "DELETE")

        return result.status_code

    def tree_get(self, path: str) -> dict:
        """Returns list of absolute paths of regular files and
        subdirectories of a directory at `path`.  Result is limited to
        1000 items.

        Raises if `path` does not point to an existing directory."""

        url = f"{self.tree_endpoint}?path={path}"

        result = call_api(url, "GET")

        if result.ok:
            return result.json()

        raise PythonAnywhereApiException(f"GET to {url} failed, got {result}{self._error_msg(result)}")
