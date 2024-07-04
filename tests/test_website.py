import getpass
import json
from urllib.parse import urljoin

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
                {"domain_name": domain_name,
                 "enabled": True}
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

    assert Website().create(domain_name=domain_name, command=command) == website_info


def test_get_returns_json_with_info_for_given_domain(
        api_responses, webapps_base_url, website_info, domain_name
):
    api_responses.add(
        responses.GET,
        url=urljoin(webapps_base_url, domain_name),
        status=200,
        body=json.dumps(website_info)
    )

    assert Website().get(domain_name=domain_name) == website_info
