import os

import pytest
import responses


@pytest.fixture
def api_responses(monkeypatch):
    with responses.RequestsMock() as r:
        yield r


@pytest.fixture(scope="function")
def api_token():
    old_token = os.environ.get("API_TOKEN")
    token = "sekrit.token"
    os.environ["API_TOKEN"] = token

    yield token

    if old_token is None:
        del os.environ["API_TOKEN"]
    else:
        os.environ["API_TOKEN"] = old_token