import sys
from typing import Any

from django.conf import settings

NOTIFICATIONS_DISABLED = False

IS_HTTPS = True

NOTIFICATIONS_GUARANTEE_DELIVERY = True

NOTIFICATIONS_API_GET_DOMAIN = "notifications_api_common.utils.get_site_domain"

TIME_LEEWAY = 0


def get_setting(name: str) -> Any:
    this_module = sys.modules[__name__]
    default = getattr(this_module, name, None)
    return getattr(settings, name, default)
