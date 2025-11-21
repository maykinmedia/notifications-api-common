import logging
import uuid

from django.utils import timezone

from notifications_api_common.settings import get_setting
from notifications_api_common.tasks import send_cloudevent

logger = logging.getLogger(__name__)


def construct_cloudevent(
    type: str,
    subject: str | None = None,
    dataref: str | None = None,
    data: dict | None = None,
):
    return {
        "id": str(uuid.uuid4()),
        "source": get_setting("NOTIFICATIONS_SOURCE"),
        "specversion": get_setting("CLOUDEVENT_SPECVERSION"),
        "type": type,
        "subject": subject,
        "time": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataref": dataref,
        "datacontenttype": "application/json",
        "data": data,
    }


def process_cloudevent(
    type: str,
    subject: str | None = None,
    dataref: str | None = None,
    data: dict | None = None,
):
    if not get_setting("NOTIFICATIONS_SOURCE"):
        msg = "Not notifying, NOTIFICATIONS_SOURCE is not set."
        logger.warning(msg)
        return

    cloudevent = construct_cloudevent(type, subject, dataref, data)
    send_cloudevent.delay(cloudevent)
