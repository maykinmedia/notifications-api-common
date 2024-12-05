from django_setup_configuration.models import ConfigurationModel, DjangoModelRef

from notifications_api_common.models import NotificationsConfig


class NotificationConfigurationModel(ConfigurationModel):
    notifications_api_service_identifier: str = DjangoModelRef(
        NotificationsConfig, "notifications_api_service", default=""
    )

    class Meta:
        django_model_refs = {
            NotificationsConfig: [
                "notification_delivery_max_retries",
                "notification_delivery_retry_backoff",
                "notification_delivery_retry_backoff_max",
            ]
        }
