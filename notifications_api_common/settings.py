import sys
from typing import Any

from django.conf import settings

NOTIFICATIONS_DISABLED = False
"""
Enable or disable notifications
"""

IS_HTTPS = True
"""
Indicate if HTTPS is used
"""

NOTIFICATIONS_GUARANTEE_DELIVERY = True
"""
Whether to raise a RuntimeError when the Notifications API is unconfigured.
"""

NOTIFICATIONS_API_GET_DOMAIN = "notifications_api_common.utils.get_site_domain"
"""
Dotpath of the function used to get the domain of the application
"""

NOTIFICATIONS_SOURCE = ""
"""
The identifier of the application to use as the source in notifications and cloudevents",
"""

CLOUDEVENT_SPECVERSION = "1.0"
"""
The used cloudevent specification version
"""

TIME_LEEWAY = 0
"""
Time validation leeway in seconds
"""

LOG_NOTIFICATIONS_IN_DB = False
"""
Indicates whether or not sent notifications should be saved to the database.
"""

NOTIFICATION_NUMBER_OF_DAYS_RETAINED = 60
"""
the number of days for which you wish to keep notifications
"""


def get_setting(name: str) -> Any:
    this_module = sys.modules[__name__]
    default = getattr(this_module, name, None)
    return getattr(settings, name, default)
