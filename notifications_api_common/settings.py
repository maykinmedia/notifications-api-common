import sys
from typing import Any

from django.conf import settings

NOTIFICATIONS_DISABLED = False

IS_HTTPS = True

NOTIFICATIONS_GUARANTEE_DELIVERY = True

SITE_DOMAIN = "example.com"


def get_setting(name: str) -> Any:
    this_module = sys.modules[__name__]
    default = getattr(this_module, name, None)
    return getattr(settings, name, default)
