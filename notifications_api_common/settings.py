import sys
from typing import Any

from django.conf import settings

NOTIFICATIONS_DISABLED = False
NOTIFICATION_DELIVERY_MAX_RETRIES = 5
NOTIFICATION_DELIVERY_RETRY_BACKOFF = 3
NOTIFICATION_DELIVERY_RETRY_BACKOFF_MAX = 48

IS_HTTPS = True


def get_setting(name: str) -> Any:
    this_module = sys.modules[__name__]
    default = getattr(this_module, name)
    return getattr(settings, name, default)
