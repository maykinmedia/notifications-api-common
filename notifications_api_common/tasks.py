import logging

import requests
from celery import shared_task
from zds_client import ClientError

from .autoretry import add_autoretry_behaviour
from .models import NotificationsConfig

logger = logging.getLogger(__name__)


class NotificationException(Exception):
    pass


@shared_task(bind=True)
def send_notification(self, message: dict) -> None:
    """
    send message to Notification API
    """
    client = NotificationsConfig.get_client()
    if client is None:
        logger.warning(
            "Could not build a client for Notifications API, not sending messages"
        )
        return

    try:
        client.create("notificaties", message)
    # any unexpected errors should show up in error-monitoring, so we only
    # catch ClientError exceptions
    except (ClientError, requests.HTTPError) as exc:
        logger.warning(
            "Could not deliver message to %s",
            client.api_root,
            exc_info=exc,
            extra={
                "notification_msg": message,
                "current_try": self.request.retries + 1,
                "final_try": self.request.retries >= self.max_retries,
            },
        )

        raise NotificationException from exc


add_autoretry_behaviour(
    send_notification,
    autoretry_for=(
        NotificationException,
        requests.RequestException,
    ),
    retry_jitter=False,
)
