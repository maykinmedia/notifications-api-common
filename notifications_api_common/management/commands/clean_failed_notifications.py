from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications_api_common.models import Notification, NotificationTypes
from notifications_api_common.settings import get_setting


class Command(BaseCommand):
    def handle(self, **options):
        date_limit = timezone.now() - timedelta(
            days=get_setting("NOTIFICATION_NUMBER_OF_DAYS_RETAINED")
        )

        notifications_filtered = Notification.objects.filter(
            type=NotificationTypes.notification, message__aanmaakdatum__lt=date_limit
        ).delete()

        cloudevents_filtered = Notification.objects.filter(
            type=NotificationTypes.cloudevent, message__time__lt=date_limit
        ).delete()

        self.stdout.write(
            str(notifications_filtered[0])
            + " notifications & responses have been deleted : "
            + str(notifications_filtered[1])
        )

        self.stdout.write(
            str(cloudevents_filtered[0])
            + " cloudevents & responses have been deleted : "
            + str(cloudevents_filtered[1])
        )
