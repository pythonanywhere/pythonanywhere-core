import getpass
import json

import pytest
import responses

from pythonanywhere_core.base import get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException
from pythonanywhere_core.website import Website
from pythonanywhere_core.exceptions import SanityException, PythonAnywhereApiException


pytestmark = pytest.mark.usefixtures("api_token")


@pytest.fixture
def websites_base_url():
    return get_api_endpoint(username=getpass.getuser(), flavor="websites")


@pytest.fixture
def domains_base_url():
    return get_api_endpoint(username=getpass.getuser(), flavor="domains")


@pytest.fixture
def domain_name():
    return "foo.bar.com"


@pytest.fixture
def command():
    return "/usr/local/bin/uvicorn --uds $DOMAIN_SOCKET main:app"


@pytest.fixture
def website_info(domain_name, command):
    return {
        "domain_name": domain_name,
        "enabled": True,
        "id": 42,
        "user": getpass.getuser(),
        "logfiles": {
            "access": f"/var/log/{domain_name}.access.log",
            "error": f"/var/log/{domain_name}.error.log",
            "server": f"/var/log/{domain_name}.server.log",
        },
        "webapp": {
            "command": command,
            "domains": [
                {
                    "domain_name": domain_name,
                    "enabled": True
                }
            ],
            "id": 42
        }
    }


def test_create_returns_json_with_created_website_info(
        api_responses, websites_base_url, website_info, domain_name, command
):
    api_responses.add(
        responses.POST, url=websites_base_url, status=201, body=json.dumps(website_info)
    )
    expected_request_body = json.dumps(
        {"domain_name": domain_name, "enabled": True, "webapp": {"command": command}}
    ).encode()

    result = Website().create(domain_name=domain_name, command=command)

    assert result == website_info
    assert api_responses.calls[0].request.body == expected_request_body, (
        "POST to create needs the payload to be passed as json field"
    )


def test_get_returns_json_with_info_for_given_domain(
        api_responses, websites_base_url, website_info, domain_name
):
    api_responses.add(
        responses.GET,
        url=f"{websites_base_url}{domain_name}/",
        status=200,
        body=json.dumps(website_info)
    )

    assert Website().get(domain_name=domain_name) == website_info


def test_list_returns_json_with_info_for_all_websites(api_responses, websites_base_url, website_info):
    api_responses.add(
        responses.GET,
        url=websites_base_url,
        status=200,
        body=json.dumps([website_info])
    )

    assert Website().list() == [website_info]


def test_reloads_website(api_responses, domain_name, websites_base_url):
    api_responses.add(
        responses.POST,
        url=f"{websites_base_url}{domain_name}/reload/",
        status=200,
        body=json.dumps({"status": "OK"})
    )

    assert Website().reload(domain_name=domain_name) == {"status": "OK"}


def test_deletes_website(api_responses, domain_name, websites_base_url):
    api_responses.add(
        responses.DELETE,
        url=f"{websites_base_url}{domain_name}/",
        status=204,
    )

    assert Website().delete(domain_name=domain_name) == {}


def test_sets_lets_encrypt_cert(api_responses, domain_name, domains_base_url):
    api_responses.add(
        responses.POST,
        url=f"{domains_base_url}{domain_name}/ssl/",
        body=json.dumps({"status": "OK"}),
        status=200
    )


    assert Website().auto_ssl(domain_name=domain_name) == {"status": "OK"}

    assert json.loads(api_responses.calls[0].request.body.decode()) == {
        "cert_type": "letsencrypt-auto-renew"
    }


def test_returns_ssl_info(api_responses, domain_name, domains_base_url):
    api_responses.add(
        responses.GET,
        url=f"{domains_base_url}{domain_name}/ssl/",
        body=json.dumps({"status": "OK"}),
        status=200
    )

    assert Website().get_ssl_info(domain_name=domain_name) == {"status": "OK"}


def test_raises_if_ssl_info_does_not_return_200(api_responses, domain_name, domains_base_url):
    api_responses.add(
        responses.GET,
        url=f"{domains_base_url}{domain_name}/ssl/",
        status=404, body="nope"
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Website().get_ssl_info(domain_name=domain_name)

    assert "GET SSL details via API failed, got" in str(e.value)
    assert "nope" in str(e.value)


def test_website_sanity_check_domain_already_exists(api_responses, websites_base_url, website_info, domain_name):
    api_responses.add(
        responses.GET,
        url=f"{websites_base_url}{domain_name}/",
        status=200,
        body=json.dumps(website_info)
    )

    with pytest.raises(SanityException) as e:
        Website().sanity_check(domain_name=domain_name, nuke=False)


def test_website_sanity_check_can_be_bypassed_with_nuke_option(api_responses, websites_base_url, website_info, domain_name):
    # Test that the sanity check does not raise an exception
    Website().sanity_check(domain_name=domain_name, nuke=True)


def test_website_sanity_check_tests_api_token_present(api_responses, websites_base_url, website_info, domain_name):
    import os 
    del os.environ["API_TOKEN"]

    # Test that the sanity check does not raise an exception
    with pytest.raises(SanityException) as e:
        Website().sanity_check(domain_name=domain_name, nuke=False)
    
    assert "Could not find your API token" in str(e.value)
