import getpass
import platform
from pythonanywhere_core import __version__

import pytest
import responses

from pythonanywhere_core.base import (
    call_api,
    get_api_endpoint,
    get_username,
    helpful_token_error_message,
)
from pythonanywhere_core.exceptions import AuthenticationError, NoTokenError


def test_get_username_returns_env_var_when_set(monkeypatch):
    monkeypatch.setenv("PYTHONANYWHERE_USERNAME", "bill")

    assert get_username() == "bill"


def test_get_username_falls_back_to_getpass(monkeypatch):
    monkeypatch.delenv("PYTHONANYWHERE_USERNAME", raising=False)

    assert get_username() == getpass.getuser()


def test_get_api_endpoint_defaults_to_pythonanywhere_dot_com_if_no_environment_variables():
    result = get_api_endpoint(username="bill", flavor="webapp")

    assert result == "https://www.pythonanywhere.com/api/v0/user/bill/webapp/"


def test_get_api_endpoint_gets_domain_from_pythonanywhere_site_and_ignores_pythonanywhere_domain_if_both_set(
        monkeypatch
):
    monkeypatch.setenv("PYTHONANYWHERE_SITE", "www.foo.com")
    monkeypatch.setenv("PYTHONANYWHERE_DOMAIN", "wibble.com")

    result = get_api_endpoint(username="bill", flavor="webapp")

    assert result == "https://www.foo.com/api/v0/user/bill/webapp/"


def test_get_api_endpoint_gets_domain_from_pythonanywhere_domain_and_adds_on_www_if_set_but_pythonanywhere_site_is_not(
        monkeypatch
):
    monkeypatch.delenv("PYTHONANYWHERE_SITE", raising=False)
    monkeypatch.setenv("PYTHONANYWHERE_DOMAIN", "foo.com")

    result = get_api_endpoint(username="bill", flavor="webapp")

    assert result == "https://www.foo.com/api/v0/user/bill/webapp/"


@pytest.mark.parametrize(
    "flavor,expected_version",
    [
        ("files", "v0"),
        ("schedule", "v0"),
        ("students", "v0"),
        ("webapps", "v0"),
        ("websites", "v1"),
    ]
)
def test_get_api_endpoint_returns_url_with_correct_api_version(flavor, expected_version):
    result = get_api_endpoint(username="bill", flavor=flavor)

    assert result == f"https://www.pythonanywhere.com/api/{expected_version}/user/bill/{flavor}/"


def test_raises_on_401(api_token, api_responses):
    url = "https://foo.com/"
    api_responses.add(responses.POST, url, status=401, body="nope")
    with pytest.raises(AuthenticationError) as e:
        call_api(url, "post")
    assert str(e.value) == "Authentication error 401 calling API: nope"




def test_raises_with_helpful_message_if_no_token_present(mocker, monkeypatch):
    mock_helpful_message = mocker.patch("pythonanywhere_core.base.helpful_token_error_message")
    mock_helpful_message.return_value = "I'm so helpful"

    monkeypatch.delenv("API_TOKEN", raising=False)

    with pytest.raises(NoTokenError) as exc:
        call_api("blah", "get")

    assert str(exc.value) == "I'm so helpful"


def test_helpful_message_inside_pythonanywhere(monkeypatch):
    monkeypatch.setenv("PYTHONANYWHERE_SITE", "www.foo.com")

    assert "Oops, you don't seem to have an API token." in helpful_token_error_message()


def test_helpful_message_outside_pythonanywhere(monkeypatch):
    monkeypatch.delenv("PYTHONANYWHERE_SITE", raising=False)

    assert "Oops, you don't seem to have an API_TOKEN environment variable set." in helpful_token_error_message()


def test_call_api_includes_user_agent_without_client_info(api_token, api_responses, monkeypatch):
    monkeypatch.delenv("PYTHONANYWHERE_CLIENT", raising=False)

    url = "https://www.pythonanywhere.com/api/v0/test"
    api_responses.add(responses.GET, url, json={"status": "ok"}, status=200)

    response = call_api(url, "GET")

    assert response.status_code == 200
    expected_ua = f"pythonanywhere-core/{__version__} (Python/{platform.python_version()})"
    assert api_responses.calls[0].request.headers["User-Agent"] == expected_ua


def test_call_api_includes_user_agent_with_client_info(api_token, api_responses, monkeypatch):
    monkeypatch.setenv("PYTHONANYWHERE_CLIENT", "pa/1.0.0")

    url = "https://www.pythonanywhere.com/api/v0/test"
    api_responses.add(responses.GET, url, json={"status": "ok"}, status=200)

    response = call_api(url, "GET")

    assert response.status_code == 200
    expected_ua = f"pythonanywhere-core/{__version__} (pa/1.0.0; Python/{platform.python_version()})"
    assert api_responses.calls[0].request.headers["User-Agent"] == expected_ua


def test_call_api_custom_headers_can_override_user_agent(api_token, api_responses):
    url = "https://www.pythonanywhere.com/api/v0/test"
    api_responses.add(responses.GET, url, json={"status": "ok"}, status=200)

    response = call_api(url, "GET", headers={"User-Agent": "custom/1.0.0"})

    assert response.status_code == 200
    assert api_responses.calls[0].request.headers["User-Agent"] == "custom/1.0.0"


def test_call_api_preserves_authorization_with_custom_headers(api_token, api_responses):
    url = "https://www.pythonanywhere.com/api/v0/test"
    api_responses.add(responses.POST, url, json={"status": "ok"}, status=200)

    response = call_api(url, "POST", headers={"X-Custom": "value"})

    assert response.status_code == 200
    assert api_responses.calls[0].request.headers["Authorization"] == f"Token {api_token}"
    assert api_responses.calls[0].request.headers["X-Custom"] == "value"
