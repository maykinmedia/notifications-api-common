from unittest.mock import patch

from django.test import override_settings

import pytest
from freezegun import freeze_time

from notifications_api_common.cloudevents import (
    construct_cloudevent,
    process_cloudevent,
)


@freeze_time("2025-01-01")
@override_settings(NOTIFICATIONS_SOURCE="openzaak.maykin.nl")
@pytest.mark.django_db()
def test_construct_cloudevent(notifications_config, requests_mock):
    cloudevent = construct_cloudevent(
        type="nl.overheid.zaken.zaak.create",
        subject="439755e0-baeb-47a2-82e5-8a5c49c2fbf9",
        data={"foo": "bar"},
    )

    assert cloudevent == {
        "id": cloudevent["id"],
        "source": "openzaak.maykin.nl",
        "specversion": "1.0",
        "type": "nl.overheid.zaken.zaak.create",
        "subject": "439755e0-baeb-47a2-82e5-8a5c49c2fbf9",
        "time": "2025-01-01T00:00:00Z",
        "dataref": None,
        "datacontenttype": "application/json",
        "data": {"foo": "bar"},
    }


@pytest.mark.django_db()
def test_process_cloudevent_no_source(notifications_config):
    process_cloudevent(
        type="nl.overheid.zaken.zaak.create",
        subject="439755e0-baeb-47a2-82e5-8a5c49c2fbf9",
        data={"foo": "bar"},
    )

    with patch("notifications_api_common.tasks.send_cloudevent.delay") as mock_task:
        process_cloudevent(
            type="nl.overheid.zaken.zaak.create",
            subject="439755e0-baeb-47a2-82e5-8a5c49c2fbf9",
            data={"foo": "bar"},
        )

    mock_task.assert_not_called()


@override_settings(NOTIFICATIONS_SOURCE="openzaak.maykin.nl")
@pytest.mark.django_db(transaction=True)
def test_process_cloudevent_success(notifications_config):
    with patch("notifications_api_common.tasks.send_cloudevent.delay") as mock_task:
        process_cloudevent(
            type="nl.overheid.zaken.zaak.create",
            subject="439755e0-baeb-47a2-82e5-8a5c49c2fbf9",
            data={"foo": "bar"},
        )

    mock_task.assert_called_once()
