import uuid

from django.utils import timezone

import structlog

from notifications_api_common.settings import get_setting
from notifications_api_common.tasks import send_cloudevent

logger = structlog.stdlib.get_logger(__name__)


def construct_cloudevent(
    event_type: str,
    subject: str | None = None,
    dataref: str | None = None,
    data: dict | None = None,
):
    return {
        "id": str(uuid.uuid4()),
        "source": get_setting("NOTIFICATIONS_SOURCE"),
        "specversion": get_setting("CLOUDEVENT_SPECVERSION"),
        "type": event_type,
        "subject": subject,
        "time": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataref": dataref,
        "datacontenttype": "application/json",
        "data": data,
    }


def process_cloudevent(
    event_type: str,
    subject: str | None = None,
    dataref: str | None = None,
    data: dict | None = None,
):
    if not get_setting("NOTIFICATIONS_SOURCE"):
        logger.warning(
            "no_notification_source_set",
        )
        return

    cloudevent = construct_cloudevent(
        event_type=event_type, subject=subject, dataref=dataref, data=data
    )
    send_cloudevent.delay(cloudevent)  # pyright: ignore
