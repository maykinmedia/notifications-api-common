from django.contrib.messages import get_messages
from django.utils.translation import gettext as _

import pytest
import requests_mock
from requests.exceptions import HTTPError, RequestException

from notifications_api_common.admin import register_webhook
from notifications_api_common.models import Subscription

from .conftest import NOTIFICATIONS_API_ROOT


@pytest.mark.django_db
def test_register_webhook_success(request_with_middleware, notifications_config):
    subscription = Subscription.objects.create(
        identifier="sub",
        callback_url="https://example.com/callback",
        client_id="client_id",
        secret="secret",
        channels=["zaken"],
    )

    with requests_mock.Mocker() as m:
        m.post(
            f"{NOTIFICATIONS_API_ROOT}abonnement",
            json={"url": "https://example.com/api/v1/abonnementen/1"},
        )
        register_webhook(object, request_with_middleware, Subscription.objects.all())

    messages = list(get_messages(request_with_middleware))

    assert len(messages) == 0

    subscription.refresh_from_db()
    assert subscription._subscription == "https://example.com/api/v1/abonnementen/1"


@pytest.mark.django_db
def test_register_webhook_request_exception(
    request_with_middleware, notifications_config
):
    Subscription.objects.create(
        identifier="sub",
        callback_url="https://example.com/callback",
        client_id="client_id",
        secret="secret",
        channels=["zaken"],
    )

    with requests_mock.Mocker() as m:
        m.post(f"{NOTIFICATIONS_API_ROOT}abonnement", exc=RequestException("exception"))
        register_webhook(object, request_with_middleware, Subscription.objects.all())

    messages = list(get_messages(request_with_middleware))

    assert len(messages) == 1
    assert messages[0].message == _(
        "Something went wrong while registering subscription for {callback_url}: {e}"
    ).format(callback_url="https://example.com/callback", e="exception")


@pytest.mark.django_db
def test_register_webhook_http_error(request_with_middleware, notifications_config):
    Subscription.objects.create(
        identifier="sub",
        callback_url="https://example.com/callback",
        client_id="client_id",
        secret="secret",
        channels=["zaken"],
    )

    with requests_mock.Mocker() as m:
        m.post(f"{NOTIFICATIONS_API_ROOT}abonnement", exc=HTTPError("400"))
        register_webhook(object, request_with_middleware, Subscription.objects.all())

    messages = list(get_messages(request_with_middleware))

    assert len(messages) == 1
    assert messages[0].message == _(
        "Something went wrong while registering subscription for {callback_url}: {e}"
    ).format(callback_url="https://example.com/callback", e="400")
