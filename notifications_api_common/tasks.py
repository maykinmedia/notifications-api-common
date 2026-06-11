import requests
import structlog
from celery import shared_task

from notifications_api_common.settings import get_setting

from .autoretry import add_autoretry_behaviour
from .models import (
    Notification,
    NotificationResponse,
    NotificationsConfig,
)

logger = structlog.stdlib.get_logger(__name__)


class NotificationException(Exception):
    pass


class CloudEventException(Exception):
    pass


@shared_task(bind=True)
def send_notification(self, message: dict, notification_id: int | None = None) -> None:
    """
    send message to Notification API


    Notifications are created before this task runs which means that if the request is successful the notification will be deleted immediately.
    Could not find a way to create the notification withing the first try and fetch it again in the retries. (self is shared across all task calls)
    """

    client = NotificationsConfig.get_client()
    if client is None:
        logger.warning("notifications_client_unavailable")
        return

    response_init_kwargs = {}
    failed = False

    try:
        response = client.post("notificaties", json=message)
        response_init_kwargs["response_status"] = response.status_code
        response.raise_for_status()
    except requests.HTTPError as exc:
        logger.warning(
            "notification_delivery_failed",
            base_url=client.base_url,
            notification_msg=message,
            current_try=self.request.retries + 1,
            final_try=self.request.retries >= self.max_retries,
            exc_info=exc,
        )

        response_init_kwargs["exception"] = response.text[:1000]
        failed = True

        raise NotificationException from exc

    except requests.RequestException as exc:
        response_init_kwargs = {"exception": str(exc)}
        failed = True
        raise

    finally:
        if get_setting("LOG_NOTIFICATIONS_IN_DB"):
            if failed:
                NotificationResponse.objects.create(
                    failed_notification_id=notification_id,
                    attempt=self.request.retries + 1,
                    **response_init_kwargs,
                )

            else:
                Notification.objects.get(pk=notification_id).delete()


@shared_task(bind=True)
def send_cloudevent(self, message: dict, notification_id: int | None = None) -> None:
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

    response_init_kwargs = {}
    failed = False

    try:
        response = client.post("cloudevents", json=message, headers=headers)
        response_init_kwargs["response_status"] = response.status_code
        response.raise_for_status()
    except requests.HTTPError as exc:
        logger.exception(
            "cloudevent_delivery_failed",
            base_url=client.base_url,
            cloudevent_msg=message,
            current_try=self.request.retries + 1,
            final_try=self.request.retries >= self.max_retries,
            exc_info=exc,
        )

        response_init_kwargs["exception"] = response.text[:1000]
        failed = True

        raise CloudEventException from exc

    except requests.RequestException as exc:
        response_init_kwargs = {"exception": str(exc)}
        failed = True
        raise

    finally:
        if get_setting("LOG_NOTIFICATIONS_IN_DB"):
            if failed:
                NotificationResponse.objects.create(
                    failed_notification_id=notification_id,
                    attempt=self.request.retries + 1,
                    **response_init_kwargs,
                )

            else:
                Notification.objects.get(pk=notification_id).delete()


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
