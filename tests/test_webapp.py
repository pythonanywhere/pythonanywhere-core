import getpass
import json

import pytest
import responses
from urllib.parse import urlencode

from pythonanywhere_core.base import get_api_endpoint, PYTHON_VERSIONS
from pythonanywhere_core.exceptions import SanityException, PythonAnywhereApiException
from pythonanywhere_core.webapp import Webapp


def test_init():
    app = Webapp("www.my-domain.com")
    assert app.domain == "www.my-domain.com"


def test_compare_equal():
    assert Webapp("www.my-domain.com") == Webapp("www.my-domain.com")


def test_compare_not_equal():
    assert Webapp("www.my-domain.com") != Webapp("www.other-domain.com")


@pytest.fixture
def domain():
    return "www.domain.com"


@pytest.fixture
def base_url():
    return get_api_endpoint().format(username=getpass.getuser(), flavor='webapps')


@pytest.fixture
def domain_url(base_url, domain):
    return f"{base_url}{domain}/"


@pytest.fixture
def webapp(domain):
    return Webapp(domain)


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

    webapp.create(
        "3.10", "/virtualenv/path", "/project/path", nuke=False
    )

    post = api_responses.calls[0]
    assert post.request.url == base_url
    assert post.request.body == urlencode(
        {"domain_name": domain, "python_version": PYTHON_VERSIONS["3.10"]}
    )
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

    webapp.create(
        "3.10", "/virtualenv/path", "/project/path", nuke=False
    )

    patch = api_responses.calls[1]
    assert patch.request.url == domain_url
    assert patch.request.body == urlencode(
        {"virtualenv_path": "/virtualenv/path", "source_directory": "/project/path"}
    )
    assert patch.request.headers["Authorization"] == f"Token {api_token}"


def test_raises_if_post_does_not_20x(api_responses, api_token, base_url, webapp):
    api_responses.add(
        responses.POST, base_url, status=500, body="an error"
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        webapp.create(
            "3.10", "/virtualenv/path", "/project/path", nuke=False
        )

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
        webapp.create(
            "3.10", "/virtualenv/path", "/project/path", nuke=False
        )

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
        webapp.create(
            "3.7", "/virtualenv/path", "/project/path", nuke=False
        )

    assert (
        "PATCH to set virtualenv path and source directory via API failed"
        in str(e.value)
    )
    assert "an error" in str(e.value)


def test_does_delete_first_for_nuke_call(api_responses, api_token, base_url, domain_url, webapp):
    api_responses.add(responses.DELETE, domain_url, status=200)
    api_responses.add(
        responses.POST, base_url, status=201, body=json.dumps({"status": "OK"})
    )
    api_responses.add(responses.PATCH, domain_url, status=200)

    webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=True)

    delete = api_responses.calls[0]
    assert delete.request.method == "DELETE"
    assert delete.request.url == domain_url
    assert delete.request.headers["Authorization"] == f"Token {api_token}"


def test_ignores_404_from_delete_call_when_nuking(api_responses, api_token, base_url, domain_url, webapp):
    api_responses.add(responses.DELETE, domain_url, status=404)
    api_responses.add(
        responses.POST, base_url, status=201, body=json.dumps({"status": "OK"})
    )
    api_responses.add(responses.PATCH, domain_url, status=200)

    webapp.create("3.10", "/virtualenv/path", "/project/path", nuke=True)
