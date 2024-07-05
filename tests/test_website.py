import getpass
import json

import pytest
import responses

from pythonanywhere_core.base import get_api_endpoint
from pythonanywhere_core.website import Website


pytestmark = pytest.mark.usefixtures("api_token")


@pytest.fixture
def webapps_base_url():
    return get_api_endpoint(username=getpass.getuser(), flavor="websites")


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
        api_responses, webapps_base_url, website_info, domain_name, command
):
    api_responses.add(
        responses.POST, url=webapps_base_url, status=201, body=json.dumps(website_info)
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
        api_responses, webapps_base_url, website_info, domain_name
):
    api_responses.add(
        responses.GET,
        url=f"{webapps_base_url}{domain_name}/",
        status=200,
        body=json.dumps(website_info)
    )

    assert Website().get(domain_name=domain_name) == website_info


def test_list_returns_json_with_info_for_all_websites(api_responses, webapps_base_url, website_info):
    api_responses.add(
        responses.GET,
        url=webapps_base_url,
        status=200,
        body=json.dumps([website_info])
    )

    assert Website().list() == [website_info]


def test_reloads_website(api_responses, domain_name, webapps_base_url):
    api_responses.add(
        responses.POST,
        url=f"{webapps_base_url}{domain_name}/reload/",
        status=200,
        body=json.dumps({"status": "OK"})
    )

    assert Website().reload(domain_name=domain_name) == {"status": "OK"}


def test_deletes_website(api_responses, domain_name, webapps_base_url):
    api_responses.add(
        responses.DELETE,
        url=f"{webapps_base_url}{domain_name}/",
        status=204,
    )

    assert Website().delete(domain_name=domain_name) == {}
