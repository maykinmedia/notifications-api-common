from pathlib import Path
from unittest.mock import patch

from django.urls import reverse

import pytest
from celery.exceptions import Retry
from freezegun import freeze_time
from zgw_consumers.test import mock_service_oas_get

from notifications_api_common.tasks import NotificationException, send_notification
from testapp.models import Person

NOTIFICATIONS_API_ROOT = "http://some-api-root/api/v1/"
TESTS_DIR = Path(__file__).parent


@freeze_time("2022-01-01")
@pytest.mark.django_db(transaction=True)
def test_api_create_person(api_client, notifications_config):
    url = reverse("person-list")
    data = {"name": "John", "address_street": "Grotestraat", "address_number": "1"}

    with patch(
        "notifications_api_common.viewsets.send_notification.delay"
    ) as mock_task:
        response = api_client.post(url, data)

    assert response.status_code == 201
    assert Person.objects.count() == 1

    person = Person.objects.get()
    assert person.name == "John"

    # check notification message
    person_url = reverse("person-detail", args=[person.pk])
    mock_task.assert_called_once_with(
        {
            "kanaal": "personen",
            "hoofdObject": f"http://testserver{person_url}",
            "resource": "person",
            "resourceUrl": f"http://testserver{person_url}",
            "actie": "create",
            "aanmaakdatum": "2022-01-01T00:00:00",
            "kenmerken": {"addressStreet": "Grotestraat"},
        }
    )


@pytest.mark.django_db()
def test_task_send_notification_success(notifications_config, requests_mock, settings):
    msg = {"foo": "bar"}
    # add mocks
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, NOTIFICATIONS_API_ROOT, "nrc")
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}notificaties", status_code=201)

    send_notification(msg)

    last_request = requests_mock.request_history[-1]
    assert last_request.url == f"{NOTIFICATIONS_API_ROOT}notificaties"
    assert last_request.method == "POST"
    assert last_request.json() == msg


@pytest.mark.django_db()
def test_task_send_notification_with_retry(
    notifications_config, requests_mock, settings
):
    msg = {"foo": "bar"}

    # add NRC mocks
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, NOTIFICATIONS_API_ROOT, "nrc")
    exc = NotificationException()
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}notificaties", exc=exc)

    with patch("notifications_api_common.tasks.send_notification.retry") as mock_retry:
        mock_retry.side_effect = Retry

        with pytest.raises(Retry):
            send_notification(msg)

    mock_retry.assert_called_with(exc=exc, countdown=3)


@pytest.mark.django_db()
def test_task_send_notification_catch_404(
    notifications_config, requests_mock, settings
):
    """
    test that 404 error will raise NotificationException,
    which can be handled by the lib users
    """
    # add NRC mocks
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, NOTIFICATIONS_API_ROOT, "nrc")
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}notificaties", status_code=404)

    with pytest.raises(NotificationException):
        send_notification({"foo": "bar"})


@pytest.mark.django_db()
def test_task_send_notification_catch_500(
    notifications_config, requests_mock, settings
):
    """
    test that 500 error will raise NotificationException,
    which can be handled by the lib users
    """
    # add NRC mocks
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, NOTIFICATIONS_API_ROOT, "nrc")
    requests_mock.post(f"{NOTIFICATIONS_API_ROOT}notificaties", status_code=500)

    with pytest.raises(NotificationException):
        send_notification({"foo": "bar"})
