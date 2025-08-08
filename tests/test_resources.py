import getpass

import pytest
import responses

from pythonanywhere_core.base import get_api_endpoint
from pythonanywhere_core.resources import CPU
from pythonanywhere_core.exceptions import PythonAnywhereApiException


@pytest.fixture
def base_url():
    return get_api_endpoint(username=getpass.getuser(), flavor="cpu")


@pytest.fixture
def cpu_api():
    return CPU()


def test_get_cpu_usage_success(api_responses, api_token, cpu_api, base_url):
    example_response = {
        'daily_cpu_limit_seconds': 100000,
        'daily_cpu_total_usage_seconds': 0.064381,
        'next_reset_time': '2025-08-09T03:26:37'
    }
    
    api_responses.add(
        responses.GET,
        base_url,
        json=example_response,
        status=200
    )

    result = cpu_api.get_cpu_usage()

    assert result == example_response


def test_get_cpu_usage_api_error(api_responses, api_token, cpu_api, base_url):
    api_responses.add(
        responses.GET,
        base_url,
        json={"detail": "Not found"},
        status=400
    )

    with pytest.raises(PythonAnywhereApiException) as exc_info:
        cpu_api.get_cpu_usage()
    
    assert "Not found" in str(exc_info.value)