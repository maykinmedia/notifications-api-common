import sys
from typing import Any

from django.conf import settings

NOTIFICATIONS_DISABLED = False

IS_HTTPS = True


def get_setting(name: str) -> Any:
    this_module = sys.modules[__name__]
    default = getattr(this_module, name)
    return getattr(settings, name, default)
