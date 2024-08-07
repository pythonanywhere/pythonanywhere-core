import getpass
import json
from urllib.parse import urljoin

import pytest
import responses

from pythonanywhere_core.base import get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException
from pythonanywhere_core.files import Files


@pytest.fixture()
def username():
    return getpass.getuser()


@pytest.fixture()
def base_url(username):
    return get_api_endpoint(username=username, flavor="files")


@pytest.fixture()
def home_dir_path(username):
    return f"/home/{username}"


@pytest.fixture()
def default_home_dir_files(base_url, home_dir_path):
    return {
        ".bashrc": {"type": "file", "url": f"{base_url}path{home_dir_path}/.bashrc"},
        ".gitconfig": {"type": "file", "url": f"{base_url}path{home_dir_path}/.gitconfig"},
        ".local": {"type": "directory", "url": f"{base_url}path{home_dir_path}/.local"},
        ".profile": {"type": "file", "url": f"{base_url}path{home_dir_path}/.profile"},
        "README.txt": {"type": "file", "url": f"{base_url}path{home_dir_path}/README.txt"},
    }


@pytest.fixture()
def readme_contents():
    return (
        b"# vim: set ft=rst:\n\nSee https://help.pythonanywhere.com/ "
        b'(or click the "Help" link at the top\nright) '
        b"for help on how to use PythonAnywhere, including tips on copying and\n"
        b"pasting from consoles, and writing your own web applications.\n"
    )


def test_path_get_returns_contents_of_directory_when_path_to_dir_provided(
        api_token, api_responses, base_url, default_home_dir_files, home_dir_path
):
    dir_url = urljoin(base_url, f"path{home_dir_path}")
    api_responses.add(
        responses.GET,
        url=dir_url,
        status=200,
        body=json.dumps(default_home_dir_files),
        headers={"Content-Type": "application/json"},
    )

    assert Files().path_get(home_dir_path) == default_home_dir_files


def test_path_get_returns_file_contents_when_file_path_provided(
        api_token, api_responses, base_url, home_dir_path, readme_contents
):
    filepath = urljoin(home_dir_path, "README.txt")
    file_url = urljoin(base_url, f"path{filepath}")
    body = readme_contents
    api_responses.add(
        responses.GET,
        url=file_url,
        status=200,
        body=body,
        headers={"Content-Type": "application/octet-stream; charset=utf-8"},
    )

    assert Files().path_get(filepath) == body


def test_path_get_raises_because_wrong_path_provided(
        api_token, api_responses, base_url
):
    wrong_path = "/foo"
    wrong_url = urljoin(base_url, f"path{wrong_path}")
    body = bytes(f'{{"detail": "No such file or directory: {wrong_path}"}}', "utf")
    api_responses.add(
        responses.GET,
        url=wrong_url,
        status=404,
        body=body,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().path_get(wrong_path)

    expected_error_msg = (
        f"GET to fetch contents of {wrong_url} failed, got <Response [404]>: "
        f"No such file or directory: {wrong_path}"
    )
    assert str(e.value) == expected_error_msg


def test_path_post_returns_200_when_existing_file_updated(
        api_token, api_responses, base_url, default_home_dir_files, home_dir_path
):
    existing_file_path = f"{home_dir_path}/README.txt"
    existing_file_url = default_home_dir_files["README.txt"]["url"]
    api_responses.add(
        responses.POST,
        url=existing_file_url,
        status=200,
    )
    content = "content".encode()

    result = Files().path_post(existing_file_path, content)

    assert result == 200


def test_path_post_returns_201_when_new_file_uploaded(
        api_token, api_responses, base_url, home_dir_path
):
    new_file_path = f"{home_dir_path}/new.txt"
    new_file_url = f"{base_url}path{home_dir_path}/new.txt"
    api_responses.add(
        responses.POST,
        url=new_file_url,
        status=201,
    )
    content = "content".encode()

    result = Files().path_post(new_file_path, content)

    assert result == 201


def test_path_post_raises_when_wrong_path(
        api_token, api_responses, base_url
):
    invalid_path = "foo"
    url_with_invalid_path = urljoin(base_url, f"path{invalid_path}")
    api_responses.add(
        responses.POST,
        url=url_with_invalid_path,
        status=404,
    )
    content = "content".encode()

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().path_post(invalid_path, content)

    expected_error_msg = (
        f"POST to upload contents to {url_with_invalid_path} failed, got <Response [404]>"
    )
    assert str(e.value) == expected_error_msg


def test_path_post_raises_when_no_contents_provided(
        api_token, api_responses, base_url, home_dir_path
):
    valid_path = f"{home_dir_path}/README.txt"
    valid_url = urljoin(base_url, f"path{valid_path}")
    body = bytes('{"detail": "You must provide a file with the name \'content\'."}', "utf")
    api_responses.add(
        responses.POST,
        url=valid_url,
        status=400,
        body=body,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().path_post(valid_path, None)

    expected_error_msg = (
        f"POST to upload contents to {valid_url} failed, got <Response [400]>: "
        "You must provide a file with the name 'content'."
    )
    assert str(e.value) == expected_error_msg


def test_path_delete_returns_204_on_successful_file_deletion(
        api_token, api_responses, base_url, home_dir_path
):
    valid_path = f"{home_dir_path}/README.txt"
    valid_url = urljoin(base_url, f"path{valid_path}")
    api_responses.add(
        responses.DELETE,
        url=valid_url,
        status=204,
    )

    result = Files().path_delete(valid_path)

    assert result == 204


def test_path_delete_raises_when_permission_denied(
        api_token, api_responses, base_url, home_dir_path
):
    home_dir_url = urljoin(base_url, f"path{home_dir_path}")
    body = bytes(
        '{"message":"You do not have permission to delete this","code":"forbidden"}',
        "utf"
    )
    api_responses.add(
        responses.DELETE,
        url=home_dir_url,
        status=403,
        body=body,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().path_delete(home_dir_path)

    expected_error_msg = (
        f"DELETE on {home_dir_url} failed, got <Response [403]>: "
        "You do not have permission to delete this"
    )
    assert str(e.value) == expected_error_msg


def test_path_delete_raises_when_wrong_path_provided(
        api_token, api_responses, base_url, home_dir_path
):
    invalid_path = "/home/some_other_user/"
    invalid_url = urljoin(base_url, f"path{invalid_path}")
    body = bytes('{"message":"File does not exist","code":"not_found"}', "utf")
    api_responses.add(
        responses.DELETE,
        url=invalid_url,
        status=404,
        body=body,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().path_delete(invalid_path)

    expected_error_msg = (
        f"DELETE on {invalid_url} failed, got <Response [404]>: "
        "File does not exist"
    )
    assert str(e.value) == expected_error_msg


def test_sharing_post_returns_url_when_path_successfully_shared_or_has_been_shared_before(
        api_token, api_responses, base_url, home_dir_path, username
):
    valid_path = f"{home_dir_path}/README.txt"
    shared_url = f"/user/{username}/shares/asdf1234/"
    sharing_url = urljoin(base_url.split("api")[0], shared_url)
    partial_response = dict(
        method=responses.POST,
        url=urljoin(base_url, "sharing/"),
        body=bytes(f'{{"url": "{shared_url}"}}', "utf"),
        headers={"Content-Type": "application/json"},
    )
    api_responses.add(**partial_response, status=201)
    api_responses.add(**partial_response, status=200)

    files = Files()
    first_share = files.sharing_post(valid_path)

    assert first_share[0] == "successfully shared"
    assert first_share[1] == sharing_url

    second_share = files.sharing_post(valid_path)

    assert second_share[0] == "was already shared"
    assert second_share[1] == sharing_url


@pytest.mark.skip(reason="not implemented in the api yet")
def test_sharing_post_raises_exception_when_path_not_provided(
        api_token, api_responses, base_url, home_dir_path
):
    url = urljoin(base_url, "sharing/")
    api_responses.add(
        responses.POST,
        url=url,
        status=400,
        body=bytes('{"error": "required field (path) not found"}', "utf"),
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().sharing_post("")

    expected_error_msg = (
        f"POST to {url} to share '' failed, got <Response [400]>: "
        "provided path is not valid"  # or similar
    )
    assert str(e.value) == expected_error_msg


def test_sharing_get_returns_sharing_url_when_path_is_shared(
        api_token, api_responses, base_url, home_dir_path, username
):
    valid_path = f"{home_dir_path}/README.txt"
    sharing_api_url = urljoin(base_url, "sharing/")
    get_url = urljoin(base_url, f"sharing/?path={valid_path}")
    shared_url_suffix = f"/user/{username}/shares/asdf1234/"
    sharing_url = urljoin(base_url.split("api")[0], shared_url_suffix)
    partial_response = dict(
        body=bytes(f'{{"url": "{shared_url_suffix}"}}', "utf"),
        headers={"Content-Type": "application/json"},
    )
    api_responses.add(**partial_response, method=responses.POST, url=sharing_api_url, status=201)
    api_responses.add(**partial_response, method=responses.GET, url=get_url, status=200)
    files = Files()
    files.sharing_post(valid_path)

    assert files.sharing_get(valid_path) == sharing_url


def test_sharing_get_returns_empty_string_when_path_not_shared(
        api_token, api_responses, base_url, home_dir_path
):
    valid_path = f"{home_dir_path}/README.txt"
    url = urljoin(base_url, f"sharing/?path={valid_path}")
    api_responses.add(method=responses.GET, url=url, status=404)

    assert Files().sharing_get(valid_path) == ""


def test_returns_204_on_sucessful_unshare(
        api_token, api_responses, base_url, home_dir_path, username
):
    valid_path = f"{home_dir_path}/README.txt"
    url = urljoin(base_url, f"sharing/?path={valid_path}")
    shared_url = f"/user/{username}/shares/asdf1234/"
    api_responses.add(method=responses.DELETE, url=url, status=204)

    assert Files().sharing_delete(valid_path) == 204


def test_returns_list_of_the_regular_files_and_subdirectories_of_a_directory(
        api_token, api_responses, base_url, default_home_dir_files, home_dir_path
):
    url = urljoin(base_url, f"tree/?path={home_dir_path}")
    default_home_dir_files["foo"] = {
        "type": "directory", "url": f"{base_url}path{home_dir_path}/foo"
    },
    tree = f'["{home_dir_path}/README.txt", "{home_dir_path}/foo/"]'
    api_responses.add(
        responses.GET,
        url=url,
        status=200,
        body=bytes(tree, "utf"),
        headers={"Content-Type": "application/json"},
    )

    result = Files().tree_get(home_dir_path)

    assert result == [f"{home_dir_path}/{file}" for file in ["README.txt", "foo/"]]

def test_raises_when_path_not_pointing_to_directory(
        api_token, api_responses, base_url, home_dir_path
):
    invalid_path = "/hmoe/oof"
    url = urljoin(base_url, f"tree/?path={invalid_path}")
    api_responses.add(
        responses.GET,
        url=url,
        status=400,
        body=bytes(f'{{"detail": "{invalid_path} is not a directory"}}', "utf"),
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().tree_get(invalid_path)

    expected_error_msg = (
        f"GET to {url} failed, got <Response [400]>: {invalid_path} is not a directory"
    )
    assert str(e.value) == expected_error_msg

def test_raises_when_path_does_not_exist(
        api_token, api_responses, base_url, home_dir_path
):
    invalid_path = "/hmoe/oof"
    url = urljoin(base_url, f"tree/?path={invalid_path}")
    api_responses.add(
        responses.GET,
        url=url,
        status=400,
        body=bytes(f'{{"detail": "{invalid_path} does not exist"}}', "utf"),
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Files().tree_get(invalid_path)

    expected_error_msg = (
        f"GET to {url} failed, got <Response [400]>: {invalid_path} does not exist"
    )
    assert str(e.value) == expected_error_msg
