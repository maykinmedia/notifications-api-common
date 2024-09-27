from django.core.management import call_command
from django.utils.translation import gettext as _

import pytest
import requests_mock

from .conftest import NOTIFICATIONS_API_ROOT


@pytest.mark.django_db
def test_register_kanalen(notifications_config):
    with requests_mock.Mocker() as m:
        m.get(f"{NOTIFICATIONS_API_ROOT}kanaal?naam=personen", json=[])
        m.post(f"{NOTIFICATIONS_API_ROOT}kanaal")
        call_command("register_kanalen")

    assert len(m.request_history) == 2

    get_request = m.request_history[0]
    assert get_request.url == f"{NOTIFICATIONS_API_ROOT}kanaal?naam=personen"

    post_request = m.request_history[1]
    assert post_request.url == f"{NOTIFICATIONS_API_ROOT}kanaal"
    assert post_request.json() == {
        "naam": "personen",
        "documentatieLink": "https://example.com/notificaties/kanalen/#personen",
        "filters": ["address_street"],
    }


@pytest.mark.django_db
def test_register_kanalen_already_exists(notifications_config):
    with requests_mock.Mocker() as m:
        m.get(
            f"{NOTIFICATIONS_API_ROOT}kanaal?naam=personen",
            json=[
                {
                    "naam": "personen",
                    "documentatieLink": "https://example.com/notificaties/kanalen/#personen",
                    "filters": ["address_street"],
                }
            ],
        )
        m.post(f"{NOTIFICATIONS_API_ROOT}kanaal")
        call_command("register_kanalen")

    assert len(m.request_history) == 1

    get_request = m.request_history[0]
    assert get_request.url == f"{NOTIFICATIONS_API_ROOT}kanaal?naam=personen"
