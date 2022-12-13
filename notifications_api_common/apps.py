from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsApiCommonConfig(AppConfig):
    name = "notifications_api_common"
    verbose_name = _("Notifications API integration")
    default_auto_field = "django.db.models.BigAutoField"
