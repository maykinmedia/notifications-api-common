from django.test import override_settings

import pytest

from notifications_api_common.models import (
    Notification,
    NotificationResponse,
)
from notifications_api_common.tasks import send_notification

from .conftest import NOTIFICATIONS_API_ROOT


@override_settings(LOG_NOTIFICATIONS_IN_DB=False)
@pytest.mark.django_db()
def test_response_error_with_logging_off_does_not_save_notification(
    notifications_config,
    requests_mock,
    settings,
    eager_send_notification,
):
    msg = {"foo": "bar"}
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}notificaties", status_code=400)

    send_notification.delay(msg)

    last_request = requests_mock.request_history[-1]
    assert last_request.url == f"{NOTIFICATIONS_API_ROOT}notificaties"
    assert last_request.method == "POST"
    assert last_request.json() == msg

    assert Notification.objects.count() == 0


@override_settings(
    LOG_NOTIFICATIONS_IN_DB=True,
)
@pytest.mark.django_db()
def test_response_error_saves_notification(
    notifications_config,
    requests_mock,
    settings,
    eager_send_notification,
):
    msg = {"foo": "bar"}
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}notificaties", status_code=400)

    send_notification.delay(msg)

    assert Notification.objects.count() == 1
    assert NotificationResponse.objects.count() == 6
    assert NotificationResponse.objects.order_by("-attempt").first().attempt == 6


@override_settings(
    LOG_NOTIFICATIONS_IN_DB=True,
)
@pytest.mark.django_db()
def test_notification_is_removed_when_request_is_successful_on_retry(
    notifications_config,
    requests_mock,
    settings,
    eager_send_notification,
):
    msg = {"foo": "bar"}
    requests_mock.post(
        f"{NOTIFICATIONS_API_ROOT}notificaties",
        [
            {"status_code": 400},
            {"status_code": 201},
        ],
    )

    send_notification.delay(msg)

    assert Notification.objects.count() == 0
    assert NotificationResponse.objects.count() == 0
