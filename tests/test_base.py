import pytest
import responses

from pythonanywhere_core.base import (
    call_api,
    get_api_endpoint,
    helpful_token_error_message,
)
from pythonanywhere_core.exceptions import AuthenticationError, NoTokenError


@pytest.fixture
def mock_requests(mocker):
    return mocker.patch("pythonanywhere_core.base.requests")


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


def test_passes_verify_from_environment(api_token, monkeypatch, mock_requests):
    monkeypatch.setenv("PYTHONANYWHERE_INSECURE_API", "true")

    call_api("url", "post", foo="bar")

    _, kwargs = mock_requests.request.call_args
    assert kwargs["verify"] is False


def test_verify_is_true_if_env_not_set(api_token, mock_requests):
    call_api("url", "post", foo="bar")

    _, kwargs = mock_requests.request.call_args
    assert kwargs["verify"] is True


def test_raises_with_helpful_message_if_no_token_present(mocker):
    mock_helpful_message = mocker.patch("pythonanywhere_core.base.helpful_token_error_message")
    mock_helpful_message.return_value = "I'm so helpful"

    with pytest.raises(NoTokenError) as exc:
        call_api("blah", "get")

    assert str(exc.value) == "I'm so helpful"


def test_helpful_message_inside_pythonanywhere(monkeypatch):
    monkeypatch.setenv("PYTHONANYWHERE_SITE", "www.foo.com")

    assert "Oops, you don't seem to have an API token." in helpful_token_error_message()


def test_helpful_message_outside_pythonanywhere():
    assert "Oops, you don't seem to have an API_TOKEN environment variable set." in helpful_token_error_message()
