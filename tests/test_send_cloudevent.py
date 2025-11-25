from pathlib import Path
from unittest.mock import patch

import pytest
from celery.exceptions import Retry

from notifications_api_common.tasks import CloudEventException, send_cloudevent

from .conftest import NOTIFICATIONS_API_ROOT

TESTS_DIR = Path(__file__).parent


@pytest.mark.django_db()
def test_task_send_cloudevent_success(notifications_config, requests_mock, settings):
    msg = {"foo": "bar"}
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}cloudevents", status_code=201)

    send_cloudevent(msg)

    last_request = requests_mock.request_history[-1]
    assert last_request.url == f"{NOTIFICATIONS_API_ROOT}cloudevents"
    assert last_request.method == "POST"
    assert last_request.json() == msg


@pytest.mark.django_db()
def test_task_send_cloudevent_with_retry(notifications_config, requests_mock, settings):
    msg = {"foo": "bar"}
    exc = CloudEventException()
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}cloudevents", exc=exc)

    with patch("notifications_api_common.tasks.send_cloudevent.retry") as mock_retry:
        mock_retry.side_effect = Retry

        with pytest.raises(Retry):
            send_cloudevent(msg)

    mock_retry.assert_called_with(exc=exc, countdown=3)


@pytest.mark.django_db()
def test_task_send_cloudevent_catch_404(notifications_config, requests_mock, settings):
    """
    test that 404 error will raise CloudEventException,
    which can be handled by the lib users
    """
    # add NRC mocks
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}cloudevents", status_code=404)

    with pytest.raises(CloudEventException):
        send_cloudevent({"foo": "bar"})


@pytest.mark.django_db()
def test_task_send_cloudevent_catch_500(notifications_config, requests_mock, settings):
    """
    test that 500 error will raise CloudEventException,
    which can be handled by the lib users
    """
    # add NRC mocks
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}cloudevents", status_code=500)

    with pytest.raises(CloudEventException):
        send_cloudevent({"foo": "bar"})
