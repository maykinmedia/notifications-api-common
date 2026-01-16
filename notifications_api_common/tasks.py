import requests
import structlog
from celery import shared_task

from .autoretry import add_autoretry_behaviour
from .models import NotificationsConfig

logger = structlog.stdlib.get_logger(__name__)


class NotificationException(Exception):
    pass


class CloudEventException(Exception):
    pass


@shared_task(bind=True)
def send_notification(self, message: dict) -> None:
    """
    send message to Notification API
    """
    client = NotificationsConfig.get_client()
    if client is None:
        logger.warning("notifications_client_unavailable")
        return

    try:
        response = client.post("notificaties", json=message)
        response.raise_for_status()
    # any unexpected errors should show up in error-monitoring, so we only
    # catch HTTPError exceptions
    except requests.HTTPError as exc:
        logger.warning(
            "notification_delivery_failed",
            base_url=client.base_url,
            notification_msg=message,
            current_try=self.request.retries + 1,
            final_try=self.request.retries >= self.max_retries,
            exc_info=exc,
        )

        raise NotificationException from exc


@shared_task(bind=True)
def send_cloudevent(self, cloudevent: dict) -> None:
    """
    send message to Notification API
    """
    client = NotificationsConfig.get_client()
    if client is None:
        logger.warning("notifications_client_unavailable")
        return

    headers = {
        "Content-Type": "application/cloudevents+json",
    }

    try:
        response = client.post("cloudevents", json=cloudevent, headers=headers)
        response.raise_for_status()
    # any unexpected errors should show up in error-monitoring, so we only
    # catch HTTPError exceptions
    except requests.HTTPError as exc:
        logger.warning(
            "cloud_event_error",
            exc_info=exc,
            extra={
                "notification_msg": cloudevent,
                "current_try": self.request.retries + 1,
                "final_try": self.request.retries >= self.max_retries,
                "base_url": client.base_url,
            },
        )
        raise CloudEventException from exc
    else:
        logger.info(
            "cloud_event_sent",
            type=cloudevent.get("type"),
            subject=cloudevent.get("subject"),
            status_code=response.status_code,
        )


add_autoretry_behaviour(
    send_notification,
    autoretry_for=(
        NotificationException,
        requests.RequestException,
    ),
    retry_jitter=False,
)

add_autoretry_behaviour(
    send_cloudevent,
    autoretry_for=(
        CloudEventException,
        requests.RequestException,
    ),
    retry_jitter=False,
)
