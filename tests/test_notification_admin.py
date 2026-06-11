from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

import requests_mock
from django_webtest import WebTest
from freezegun import freeze_time
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from notifications_api_common.models import (
    Notification,
    NotificationResponse,
    NotificationsConfig,
    NotificationTypes,
)
from notifications_api_common.tasks import send_cloudevent, send_notification


@freeze_time("2022-01-01T12:00:00")
@override_settings(
    LOG_NOTIFICATIONS_IN_DB=True,
)
class NotificationAdminWebTest(WebTest):
    maxdiff = None

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )

        service = Service.objects.create(
            api_root="http://some-api-root/api/v1/",
            api_type=APITypes.nrc,
            secret="secret",
        )
        config = NotificationsConfig.get_solo()
        config.notifications_api_service = service
        config.save()

        cls._patch_send_notification = patch(
            "notifications_api_common.tasks.send_notification.delay",
            side_effect=lambda msg, nid: send_notification.apply(args=[msg, nid]),
        )
        cls._patch_send_cloudevent = patch(
            "notifications_api_common.tasks.send_cloudevent.delay",
            side_effect=lambda msg, nid: send_cloudevent.apply(args=[msg, nid]),
        )
        cls._patch_backoff = patch(
            "notifications_api_common.autoretry.get_exponential_backoff_interval",
            return_value=0,
        )

        cls._patch_send_notification.start()
        cls._patch_send_cloudevent.start()
        cls._patch_backoff.start()

        cls.addClassCleanup(cls._patch_send_notification.stop)
        cls.addClassCleanup(cls._patch_send_cloudevent.stop)
        cls.addClassCleanup(cls._patch_backoff.stop)

    def test_resend_notification(self):
        msg = {"foo": "bar"}
        notification = Notification.objects.create(
            message=msg, type=NotificationTypes.notification
        )
        NotificationResponse.objects.create(failed_notification=notification)

        with requests_mock.mock() as m:
            m.post("http://some-api-root/api/v1/notificaties", status_code=201)

            response = self.app.get(
                reverse(
                    "admin:notifications_api_common_notification_change",
                    args=(notification.pk,),
                ),
                user=self.user,
            )

            form = response.forms["notification_form"]
            response = form.submit()

        self.assertEqual(m.call_count, 1)
        self.assertEqual(m.last_request.path, "/api/v1/notificaties")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(NotificationResponse.objects.count(), 0)

    def test_resend_cloudevent(self):
        msg = {"foo": "bar"}
        notification = Notification.objects.create(
            message=msg, type=NotificationTypes.cloudevent
        )
        NotificationResponse.objects.create(failed_notification=notification)

        with requests_mock.mock() as m:
            m.post("http://some-api-root/api/v1/cloudevents", status_code=201)

            response = self.app.get(
                reverse(
                    "admin:notifications_api_common_notification_change",
                    args=(notification.pk,),
                ),
                user=self.user,
            )

            form = response.forms["notification_form"]
            response = form.submit()

        self.assertEqual(m.call_count, 1)
        self.assertEqual(m.last_request.path, "/api/v1/cloudevents")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(NotificationResponse.objects.count(), 0)

    def test_resend_notification_action(self):
        """
        Verify that a notification is scheduled when it is saved via the admin
        """
        msg = {"foo": "bar"}
        notification1 = Notification.objects.create(
            message=msg, type=NotificationTypes.cloudevent
        )
        NotificationResponse.objects.create(failed_notification=notification1)
        notification2 = Notification.objects.create(
            message=msg, type=NotificationTypes.notification
        )
        NotificationResponse.objects.create(failed_notification=notification2)

        notification3 = Notification.objects.create(
            message=msg, type=NotificationTypes.notification
        )
        NotificationResponse.objects.create(failed_notification=notification3)

        with requests_mock.mock() as m:
            m.post("http://some-api-root/api/v1/notificaties", status_code=201)
            m.post("http://some-api-root/api/v1/cloudevents", status_code=201)

            response = self.app.get(
                reverse("admin:notifications_api_common_notification_changelist"),
                user=self.user,
            )

            form = response.forms["changelist-form"]
            form["action"] = "resend_notifications"
            form["_selected_action"] = [notification1.pk, notification2.pk]

            response = form.submit()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(m.call_count, 2)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(NotificationResponse.objects.count(), 1)

    def test_resend_notification_fails(self):
        msg = {"foo": "bar"}
        notification = Notification.objects.create(
            message=msg, type=NotificationTypes.notification
        )
        NotificationResponse.objects.create(failed_notification=notification)

        with requests_mock.mock() as m:
            m.post("http://some-api-root/api/v1/notificaties", status_code=400)

            response = self.app.get(
                reverse(
                    "admin:notifications_api_common_notification_change",
                    args=(notification.pk,),
                ),
                user=self.user,
            )

            form = response.forms["notification_form"]
            response = form.submit()

        self.assertEqual(m.call_count, 6)
        self.assertEqual(m.last_request.path, "/api/v1/notificaties")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(NotificationResponse.objects.count(), 7)

    def test_resend_cloudevent_fails(self):
        msg = {"foo": "bar"}
        notification = Notification.objects.create(
            message=msg, type=NotificationTypes.cloudevent
        )
        NotificationResponse.objects.create(failed_notification=notification)

        with requests_mock.mock() as m:
            m.post("http://some-api-root/api/v1/cloudevents", status_code=400)

            response = self.app.get(
                reverse(
                    "admin:notifications_api_common_notification_change",
                    args=(notification.pk,),
                ),
                user=self.user,
            )

            form = response.forms["notification_form"]
            response = form.submit()

        self.assertEqual(m.call_count, 6)
        self.assertEqual(m.last_request.path, "/api/v1/cloudevents")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(NotificationResponse.objects.count(), 7)
