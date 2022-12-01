import logging

import celery
import requests
from zds_client import ClientError

from .models import NotificationsConfig

logger = logging.getLogger(__name__)


class ConfigTask(celery.Task):
    """
    add retry options from NotificationsConfig into the task instance
    """

    def __init__(self):
        config = NotificationsConfig.get_solo()

        self.max_retries = config.notification_delivery_max_retries
        self.retry_backoff = config.notification_delivery_retry_backoff
        self.retry_backoff_max = config.notification_delivery_retry_backoff_max


class NotificationException(Exception):
    pass


@celery.current_app.task(
    bind=True,
    autoretry_for=(NotificationException, requests.RequestException),
    base=ConfigTask,
)
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
    except ClientError as exc:
        logger.warning(
            "Could not deliver message to %s",
            client.base_url,
            exc_info=True,
            extra={
                "notification_msg": message,
                "current_try": self.request.retries + 1,
                "final_try": self.request.retries >= self.max_retries,
            },
        )

        raise NotificationException from exc
