import getpass
import json
from datetime import datetime
from pathlib import Path

import pytest
import responses
from dateutil.tz import tzutc
from urllib.parse import urlencode

from pythonanywhere_core.base import get_api_endpoint, PYTHON_VERSIONS
from pythonanywhere_core.exceptions import SanityException, PythonAnywhereApiException
from pythonanywhere_core.webapp import Webapp


@pytest.fixture
def base_url():
    return get_api_endpoint(username=getpass.getuser(), flavor="webapps")


@pytest.fixture
def domain():
    return "www.domain.com"


@pytest.fixture()
def base_file_url():
    return get_api_endpoint(username=getpass.getuser(), flavor='files')


@pytest.fixture
def base_log_url(base_file_url, domain):
    return f"{base_file_url}path/var/log/{domain}"

@pytest.fixture
def domain_url(base_url, domain):
    return f"{base_url}{domain}/"


@pytest.fixture
def ssl_url(domain_url):
    return f"{domain_url}ssl/"


@pytest.fixture
def webapp(domain):
    return Webapp(domain)


def test_init(base_url, domain, domain_url, webapp):
    assert webapp.domain == domain
    assert webapp.webapps_url == base_url
    assert webapp.domain_url == domain_url


def test_compare_equal():
    assert Webapp("www.my-domain.com") == Webapp("www.my-domain.com")


def test_compare_not_equal():
    assert Webapp("www.my-domain.com") != Webapp("www.other-domain.com")


def test_does_not_complain_if_api_token_exists(api_token, api_responses, domain_url, webapp):
    api_responses.add(responses.GET, domain_url, status=404)
    webapp.sanity_checks(nuke=False)  # should not raise


def test_raises_if_no_api_token_exists(api_responses, no_api_token, webapp):
    with pytest.raises(SanityException) as e:
        webapp.sanity_checks(nuke=False)
    assert "Could not find your API token" in str(e.value)


def test_raises_if_webapp_already_exists(api_token, api_responses, domain, domain_url, webapp):
    api_responses.add(
        responses.GET,
        domain_url,
        status=200,
        body=json.dumps({"id": 1, "domain_name": domain}),
    )

    with pytest.raises(SanityException) as e:
        webapp.sanity_checks(nuke=False)

    assert f"You already have a webapp for {domain}" in str(e.value)
    assert "nuke" in str(e.value)


def test_does_not_raise_if_no_webapp(api_token, api_responses, domain_url, webapp):
    api_responses.add(responses.GET, domain_url, status=404)
    webapp.sanity_checks(nuke=False)  # should not raise


def test_nuke_option_overrides_all_but_token_check(
    api_token, api_responses, domain, fake_home, virtualenvs_folder, webapp
):
    (fake_home / domain).mkdir()
    (virtualenvs_folder / domain).mkdir()

    webapp.sanity_checks(nuke=True)  # should not raise


def test_does_post_to_create_webapp(api_responses, api_token, base_url, domain, domain_url, webapp):
    api_responses.add(
        responses.POST,
        base_url,
        status=201,
        body=json.dumps({"status": "OK"}),
    )
    api_responses.add(responses.PATCH, domain_url, status=200)

    webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=False)

    post = api_responses.calls[0]
    assert post.request.url == base_url
    assert post.request.body == urlencode({"domain_name": domain, "python_version": PYTHON_VERSIONS["3.10"]})
    assert post.request.headers["Authorization"] == f"Token {api_token}"


def test_does_patch_to_update_virtualenv_path_and_source_directory(
    api_responses, api_token, base_url, domain_url, webapp
):
    api_responses.add(
        responses.POST,
        base_url,
        status=201,
        body=json.dumps({"status": "OK"}),
    )
    api_responses.add(responses.PATCH, domain_url, status=200)

    webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=False)

    patch = api_responses.calls[1]
    assert patch.request.url == domain_url
    assert patch.request.body == urlencode({"virtualenv_path": "/virtualenv/path", "source_directory": "/project/path"})
    assert patch.request.headers["Authorization"] == f"Token {api_token}"


def test_raises_if_post_to_create_does_not_20x(api_responses, api_token, base_url, webapp):
    api_responses.add(responses.POST, base_url, status=500, body="an error")

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=False)

    assert "POST to create webapp via API failed" in str(e.value)
    assert "an error" in str(e.value)


def test_raises_if_post_returns_a_200_with_status_error(api_responses, api_token, base_url, webapp):
    api_responses.add(
        responses.POST,
        base_url,
        status=200,
        body=json.dumps(
            {
                "status": "ERROR",
                "error_type": "bad",
                "error_message": "bad things happened",
            }
        ),
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=False)

    assert "POST to create webapp via API failed" in str(e.value)
    assert "bad things happened" in str(e.value)


def test_raises_if_patch_does_not_20x(api_responses, api_token, base_url, domain_url, webapp):
    api_responses.add(
        responses.POST,
        base_url,
        status=201,
        body=json.dumps({"status": "OK"}),
    )
    api_responses.add(
        responses.PATCH,
        domain_url,
        status=400,
        json={"message": "an error"},
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.create("3.7", "/virtualenv/path", "/project/path", nuke=False)

    assert "PATCH to set virtualenv path and source directory via API failed" in str(e.value)
    assert "an error" in str(e.value)


def test_does_delete_first_for_nuke_call(api_responses, api_token, base_url, domain_url, webapp):
    api_responses.add(responses.DELETE, domain_url, status=200)
    api_responses.add(responses.POST, base_url, status=201, body=json.dumps({"status": "OK"}))
    api_responses.add(responses.PATCH, domain_url, status=200)

    webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=True)

    delete = api_responses.calls[0]
    assert delete.request.method == "DELETE"
    assert delete.request.url == domain_url
    assert delete.request.headers["Authorization"] == f"Token {api_token}"


def test_ignores_404_from_delete_call_when_nuking(api_responses, api_token, base_url, domain_url, webapp):
    api_responses.add(responses.DELETE, domain_url, status=404)
    api_responses.add(responses.POST, base_url, status=201, body=json.dumps({"status": "OK"}))
    api_responses.add(responses.PATCH, domain_url, status=200)

    webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=True)


def test_create_static_file_mapping_posts_correctly(api_token, api_responses, domain_url, webapp):
    static_files_url = f"{domain_url}static_files/"
    api_responses.add(responses.POST, static_files_url, status=201)

    webapp.create_static_file_mapping("/assets/", "/project/assets")

    post = api_responses.calls[0]
    assert post.request.url == static_files_url
    assert post.request.headers["content-type"] == "application/json"
    assert post.request.headers["Authorization"] == f"Token {api_token}"
    assert json.loads(post.request.body.decode("utf8")) == {
        "url": "/assets/",
        "path": "/project/assets",
    }


def test_adds_default_static_files_mappings(mocker, webapp):
    mock_create = mocker.patch.object(webapp, "create_static_file_mapping")

    project_path = "/directory/path"
    webapp.add_default_static_files_mappings(project_path)

    mock_create.assert_has_calls(
        [
            mocker.call("/static/", Path(project_path) / "static"),
            mocker.call("/media/", Path(project_path) / "media"),
        ]
    )



def test_does_post_to_reload_url(api_responses, api_token, domain_url, webapp):
    reload_url = f"{domain_url}reload/"
    api_responses.add(responses.POST, reload_url, status=200)

    webapp.reload()

    post = api_responses.calls[0]
    assert post.request.url == reload_url
    assert post.request.body is None
    assert post.request.headers["Authorization"] == f"Token {api_token}"


def test_raises_if_post_does_not_20x_that_is_not_a_cname_error(api_responses, api_token, domain_url, webapp):
    reload_url = f"{domain_url}reload/"
    api_responses.add(responses.POST, reload_url, status=404, body="nope")

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.reload()

    assert "POST to reload webapp via API failed" in str(e.value)
    assert "nope" in str(e.value)


def test_does_not_raise_if_post_responds_with_a_cname_error(api_responses, api_token, domain_url, webapp):
    reload_url = f"{domain_url}reload/"
    api_responses.add(
        responses.POST,
        reload_url,
        status=409,
        json={"status": "error", "error": "cname_error"},
    )

    webapp.reload()  # Should not raise


def test_does_post_to_ssl_url(api_responses, api_token, domain_url, webapp):
    ssl_url = f"{domain_url}ssl/"
    api_responses.add(responses.POST, ssl_url, status=200)
    certificate = "certificate data"
    private_key = "private key data"

    webapp.set_ssl(certificate, private_key)

    post = api_responses.calls[0]
    assert post.request.url == ssl_url
    assert json.loads(post.request.body.decode("utf8")) == {
        "private_key": "private key data",
        "cert": "certificate data",
    }
    assert post.request.headers["Authorization"] == f"Token {api_token}"


def test_raises_if_post_to_ssl_does_not_20x(api_responses, api_token, ssl_url, webapp):
    api_responses.add(responses.POST, ssl_url, status=404, body="nope")

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.set_ssl("foo", "bar")

    assert "POST to set SSL details via API failed" in str(e.value)
    assert "nope" in str(e.value)


def test_returns_json_from_server_having_parsed_expiry_with_z_for_utc_and_no_separators(
    api_responses, api_token, ssl_url, webapp
):
    api_responses.add(
        responses.GET,
        ssl_url,
        status=200,
        body=json.dumps(
            {
                "not_after": "20180824T171623Z",
                "issuer_name": "PythonAnywhere test CA",
                "subject_name": "www.mycoolsite.com",
                "subject_alternate_names": ["www.mycoolsite.com", "mycoolsite.com"],
            }
        ),
    )

    assert webapp.get_ssl_info() == {
        "not_after": datetime(2018, 8, 24, 17, 16, 23, tzinfo=tzutc()),
        "issuer_name": "PythonAnywhere test CA",
        "subject_name": "www.mycoolsite.com",
        "subject_alternate_names": ["www.mycoolsite.com", "mycoolsite.com"],
    }

    get = api_responses.calls[0]
    assert get.request.method == "GET"
    assert get.request.url == ssl_url
    assert get.request.headers["Authorization"] == f"Token {api_token}"


def test_returns_json_from_server_having_parsed_expiry_with_timezone_offset_and_separators(
    api_responses, api_token, ssl_url, webapp
):
    api_responses.add(
        responses.GET,
        ssl_url,
        status=200,
        body=json.dumps(
            {
                "not_after": "2018-08-24T17:16:23+00:00",
                "issuer_name": "PythonAnywhere test CA",
                "subject_name": "www.mycoolsite.com",
                "subject_alternate_names": ["www.mycoolsite.com", "mycoolsite.com"],
            }
        ),
    )

    assert webapp.get_ssl_info() == {
        "not_after": datetime(2018, 8, 24, 17, 16, 23, tzinfo=tzutc()),
        "issuer_name": "PythonAnywhere test CA",
        "subject_name": "www.mycoolsite.com",
        "subject_alternate_names": ["www.mycoolsite.com", "mycoolsite.com"],
    }

    get = api_responses.calls[0]
    assert get.request.method == "GET"
    assert get.request.url == ssl_url
    assert get.request.headers["Authorization"] == f"Token {api_token}"


def test_raises_if_get_does_not_return_200(api_responses, api_token, ssl_url, webapp):
    api_responses.add(responses.GET, ssl_url, status=404, body="nope")

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.get_ssl_info()

    assert "GET SSL details via API failed, got" in str(e.value)
    assert "nope" in str(e.value)


def test_delete_current_access_log(api_responses, api_token, base_log_url, webapp):
    expected_url = f"{base_log_url}.access.log/"
    api_responses.add(responses.DELETE, expected_url, status=200)

    webapp.delete_log(log_type="access")

    post = api_responses.calls[0]
    assert post.request.url == expected_url
    assert post.request.body is None
    assert post.request.headers["Authorization"] == f"Token {api_token}"


def test_delete_old_access_log(api_responses, api_token, base_log_url, webapp):
    expected_url = f"{base_log_url}.access.log.1/"
    api_responses.add(responses.DELETE, expected_url, status=200)

    webapp.delete_log(log_type="access", index=1)

    post = api_responses.calls[0]
    assert post.request.url == expected_url
    assert post.request.body is None
    assert post.request.headers["Authorization"] == f"Token {api_token}"


def test_raises_if_log_delete_does_not_20x(api_responses, api_token, base_log_url, webapp):
    expected_url = f"{base_log_url}.access.log/"
    api_responses.add(responses.DELETE, expected_url, status=404, body="nope")

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.delete_log(log_type="access")

    assert "DELETE log file via API failed" in str(e.value)
    assert "nope" in str(e.value)


def test_get_list_of_logs(api_responses, api_token, base_file_url, domain, webapp):
    expected_url = f"{base_file_url}tree/?path=/var/log/"
    api_responses.add(
        responses.GET,
        expected_url,
        status=200,
        body=json.dumps(
            [
                "/var/log/blah",
                f"/var/log/{domain}.access.log",
                f"/var/log/{domain}.access.log.1",
                f"/var/log/{domain}.access.log.2.gz",
                f"/var/log/{domain}.error.log",
                f"/var/log/{domain}.error.log.1",
                f"/var/log/{domain}.error.log.2.gz",
                f"/var/log/{domain}.server.log",
                f"/var/log/{domain}.server.log.1",
                f"/var/log/{domain}.server.log.2.gz",
            ]
        ),
    )

    logs = webapp.get_log_info()

    post = api_responses.calls[0]
    assert post.request.url == expected_url
    assert post.request.headers["Authorization"] == f"Token {api_token}"
    assert logs == {"access": [0, 1, 2], "error": [0, 1, 2], "server": [0, 1, 2]}


def test_raises_if_get_does_not_20x(api_responses, api_token, base_file_url, webapp):
    expected_url = f"{base_file_url}tree/?path=/var/log/"
    api_responses.add(responses.GET, expected_url, status=404, body="nope")

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.get_log_info()

    assert "GET log files info via API failed" in str(e.value)
    assert "nope" in str(e.value)
