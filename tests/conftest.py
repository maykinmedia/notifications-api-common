from unittest.mock import patch

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

import pytest
from rest_framework.test import APIClient
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from notifications_api_common.models import NotificationsConfig
from notifications_api_common.tasks import (
    send_cloudevent,
    send_notification,
)
from testapp import urls  # noqa

NOTIFICATIONS_API_ROOT = "http://some-api-root/api/v1/"


def dummy_get_response(request):
    raise NotImplementedError()


@pytest.fixture()
def request_with_middleware(rf):
    request = rf.get("/")
    SessionMiddleware(get_response=dummy_get_response).process_request(request)
    MessageMiddleware(get_response=dummy_get_response).process_request(request)
    return request


@pytest.fixture()
def notifications_config():
    service = Service.objects.create(
        api_root="http://some-api-root/api/v1/",
        api_type=APITypes.nrc,
        secret="super-secret",
    )
    config = NotificationsConfig.get_solo()
    config.notifications_api_service = service
    config.save()
    return config


@pytest.fixture()
def api_client() -> APIClient:
    client = APIClient()
    return client


@pytest.fixture
def eager_send_notification():
    with patch(
        "notifications_api_common.tasks.send_notification.delay",
        side_effect=lambda msg, nid=None: send_notification.apply(args=[msg, nid]),
    ):
        yield


@pytest.fixture
def eager_send_cloudevent():
    with patch(
        "notifications_api_common.tasks.send_cloudevent.delay",
        side_effect=lambda msg, nid=None: send_cloudevent.apply(args=[msg, nid]),
    ):
        yield
