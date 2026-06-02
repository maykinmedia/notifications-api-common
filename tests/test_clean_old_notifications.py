from datetime import datetime, timedelta

from django.core.management import call_command
from django.test import override_settings

import pytest

from notifications_api_common.models import (
    Notification,
    NotificationResponse,
    NotificationTypes,
)


def _create_notif(type: NotificationTypes, date: str):
    notif = Notification.objects.create(
        message={
            "aanmaakdatum" if type == NotificationTypes.notification else "time": date
        },
        type=type,
    )
    NotificationResponse.objects.create(failed_notification=notif)

    return notif


@override_settings(NOTIFICATION_NUMBER_OF_DAYS_RETAINED=30)
@pytest.mark.django_db()
def test_objects_are_deleted():
    in_month = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    out_month = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    _create_notif(NotificationTypes.notification, in_month)
    _create_notif(NotificationTypes.notification, out_month)
    _create_notif(NotificationTypes.cloudevent, in_month)
    _create_notif(NotificationTypes.cloudevent, out_month)

    assert Notification.objects.count() == 4
    assert NotificationResponse.objects.count() == 4

    call_command("clean_old_notifications")

    assert Notification.objects.count() == 2
    assert NotificationResponse.objects.count() == 2


@override_settings(NOTIFICATION_NUMBER_OF_DAYS_RETAINED=60)
@pytest.mark.django_db()
def test_change_of_period():
    in_month = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    out_month = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    _create_notif(NotificationTypes.notification, in_month)
    _create_notif(NotificationTypes.notification, out_month)
    _create_notif(NotificationTypes.cloudevent, in_month)
    _create_notif(NotificationTypes.cloudevent, out_month)

    assert Notification.objects.count() == 4
    assert NotificationResponse.objects.count() == 4

    call_command("clean_old_notifications")

    assert Notification.objects.count() == 4
    assert NotificationResponse.objects.count() == 4
