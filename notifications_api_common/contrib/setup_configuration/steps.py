from django_setup_configuration.configuration import BaseConfigurationStep
from zgw_consumers.models import Service

from notifications_api_common.models import NotificationsConfig

from .models import NotificationConfigurationModel


def get_service(slug: str) -> Service:
    """
    Try to find a Service and re-raise DoesNotExist with the identifier
    to make debugging easier
    """
    try:
        return Service.objects.get(slug=slug)
    except Service.DoesNotExist as e:
        raise Service.DoesNotExist(f"{str(e)} (identifier = {slug})")


class NotificationConfigurationStep(
    BaseConfigurationStep[NotificationConfigurationModel]
):
    """
    Configure settings for Notificaties API
    """

    verbose_name = "Configuration for Notificaties API"
    config_model = NotificationConfigurationModel
    namespace = "notifications_config"
    enable_setting = "notifications_config_enable"

    def execute(self, model: NotificationConfigurationModel):
        config = NotificationsConfig.get_solo()

        if identifier := model.notifications_api_service_identifier:
            config.notifications_api_service = get_service(identifier)

        if model.notification_delivery_max_retries:
            config.notification_delivery_max_retries = (
                model.notification_delivery_max_retries
            )
        if model.notification_delivery_retry_backoff:
            config.notification_delivery_retry_backoff = (
                model.notification_delivery_retry_backoff
            )
        if model.notification_delivery_retry_backoff_max:
            config.notification_delivery_retry_backoff_max = (
                model.notification_delivery_retry_backoff_max
            )

        config.save()
