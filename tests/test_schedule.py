import getpass
import json

import pytest
import responses

from pythonanywhere_core.base import get_api_endpoint
from pythonanywhere_core.exceptions import PythonAnywhereApiException
from pythonanywhere_core.schedule import Schedule


@pytest.fixture
def task_base_url():
    return get_api_endpoint(username=getpass.getuser(), flavor="schedule")


@pytest.fixture
def task_specs():
    username = getpass.getuser()
    return {
        "can_enable": False,
        "command": "echo foo",
        "enabled": True,
        "expiry": None,
        "extend_url": f"/user/{username}/schedule/task/123/extend",
        "hour": 16,
        "id": 123,
        "interval": "daily",
        "logfile": "/user/{username}/files/var/log/tasklog-126708-daily-at-1600-echo_foo.log",
        "minute": 0,
        "printable_time": "16:00",
        "url": f"/api/v0/user/{username}/schedule/123",
        "user": username,
    }


@pytest.fixture
def base_task_params():
    return {
        "command": "echo foo",
        "enabled": True,
        "minute": 0,
    }


@pytest.fixture
def hourly_task_params(base_task_params):
    return {
        **base_task_params,
        "interval": "hourly",
        "minute": 0,
    }


@pytest.fixture
def daily_task_params(base_task_params):
    return {
        **base_task_params,
        "interval": "daily",
        "hour": 16,
    }


def test_creates_daily_task(
        api_token, api_responses, task_specs, daily_task_params, task_base_url
):
    api_responses.add(
        responses.POST, url=task_base_url, status=201, body=json.dumps(task_specs)
    )

    assert Schedule().create(daily_task_params) == task_specs


def test_creates_hourly_task(
        api_token, api_responses, task_specs, hourly_task_params, task_base_url
):
    hourly_specs = {"hour": None, "interval": "hourly", "printable_time": "00 minutes past"}
    task_specs.update(hourly_specs)
    api_responses.add(
        responses.POST, url=task_base_url, status=201, body=json.dumps(task_specs)
    )

    assert Schedule().create(hourly_task_params) == task_specs


@pytest.mark.parametrize("status_code, body", [
    (200, '{"task_id": 42}'),
    (202, '{"status": "accepted"}'),
    (204, ""),
    (400, '{"detail": "Invalid task"}'),
    (403, '{"detail": "Forbidden"}'),
    (500, '{"detail": "Server error"}'),
    (500, "Non-JSON server error"),
])
def test_create_raises_unless_response_is_201(
        api_token, api_responses, task_base_url, daily_task_params, status_code, body
):
    api_responses.add(responses.POST, task_base_url, status=status_code, body=body)

    with pytest.raises(PythonAnywhereApiException) as exc:
        Schedule().create(daily_task_params)

    assert str(status_code) in str(exc.value)
    assert body in str(exc.value)
    assert len(api_responses.calls) == 1


def test_raises_because_missing_params(api_token, api_responses, task_base_url):
    body = (
        '{"interval":["This field is required."],"command":["This field is required."],'
        '"minute":["This field is required."]}'
    )
    api_responses.add(responses.POST, url=task_base_url, status=400, body=body)

    with pytest.raises(PythonAnywhereApiException) as e:
        Schedule().create({})

    expected_error_msg = (
        f"POST to set new task via API failed, got <Response [400]>: {body}"
    )
    assert str(e.value) == expected_error_msg


def test_deletes_task(api_token, api_responses, task_base_url):
    url = f"{task_base_url}42/"
    api_responses.add(responses.DELETE, url=url, status=204)

    result = Schedule().delete(42)

    post = api_responses.calls[0]
    assert post.request.url == url
    assert post.request.body is None
    assert result is True


def test_raises_because_attempt_to_delete_nonexisting_task(api_token, api_responses, task_base_url):
    body = '{"detail": "Not fount."}'
    api_responses.add(
        responses.DELETE, url=f"{task_base_url}42/", status=404, body=body
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Schedule().delete(42)

    assert (
        str(e.value)
        == f"DELETE via API on task 42 failed, got <Response [404]>: {body}"
    )


def test_returns_spec_dict(api_token, api_responses, task_base_url, task_specs):
    api_responses.add(
        responses.GET,
        url=f"{task_base_url}123/",
        status=200,
        body=json.dumps(task_specs),
    )

    assert Schedule().get_specs(123) == task_specs


def test_raises_because_attempt_to_get_nonexisting_task(api_token, api_responses, task_base_url):
    body = '{"detail":"Not found."}'
    api_responses.add(
        responses.GET, url=f"{task_base_url}42/", status=404, body=body
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Schedule().get_specs(42)

    expected_error_msg = (
        f"Could not get task with id 42. Got result <Response [404]>: {body}"
    )
    assert str(e.value) == expected_error_msg


@pytest.mark.parametrize("fake_specs", [[], [{"fake": "specs"}, {"and": "more"}]])
def test_returns_tasks_list(api_token, api_responses, task_base_url, fake_specs):
    api_responses.add(
        responses.GET, url=task_base_url, status=200, body=json.dumps(fake_specs),
    )

    assert Schedule().get_list() == fake_specs


@pytest.mark.parametrize("status_code, body", [
    (201, "[]"),
    (202, '{"status": "accepted"}'),
    (204, ""),
    (403, '{"detail": "Forbidden"}'),
    (429, '{"detail": "Throttled"}'),
    (500, '{"detail": "Server error"}'),
    (500, "Non-JSON server error"),
])
def test_list_raises_unless_response_is_200(
        api_token, api_responses, task_base_url, status_code, body
):
    api_responses.add(responses.GET, task_base_url, status=status_code, body=body)

    with pytest.raises(PythonAnywhereApiException) as exc:
        Schedule().get_list()

    assert str(status_code) in str(exc.value)
    assert body in str(exc.value)


def test_updates_daily_task(
    api_token, api_responses, task_specs, daily_task_params, task_base_url
):
    api_responses.add(
        responses.PATCH,
        url=f"{task_base_url}123/",
        status=200,
        body=json.dumps(task_specs),
    )

    assert Schedule().update(123, daily_task_params) == task_specs


def test_raises_when_wrong_params(
    api_token, api_responses, task_specs, daily_task_params, task_base_url
):
    body = '{"non_field_errors":["Hourly tasks must not have an hour."]}'
    api_responses.add(
        responses.PATCH, url=f"{task_base_url}1/", status=400, body=body
    )

    with pytest.raises(PythonAnywhereApiException) as e:
        Schedule().update(1, {"hour": 23})

    assert str(e.value) == f"Could not update task 1. Got <Response [400]>: {body}"
