from django_setup_configuration.models import ConfigurationModel, DjangoModelRef
from pydantic import UUID4, Field

from notifications_api_common.models import NotificationsConfig, Subscription


class NotificationConfigurationModel(ConfigurationModel):
    notifications_api_service_identifier: str = DjangoModelRef(
        NotificationsConfig,
        "notifications_api_service",
        examples=["notificaties-api"],
        default=...,
    )

    class Meta:
        django_model_refs = {
            NotificationsConfig: [
                "notification_delivery_max_retries",
                "notification_delivery_retry_backoff",
                "notification_delivery_retry_backoff_max",
                "notification_delivery_base_factor",
            ]
        }


class SubscriptionConfigurationItem(ConfigurationModel):
    uuid: UUID4 = Field(
        description="The UUID for this subscription. Must match the UUID of the corresponding `Abonnement` in Open Notificaties.",
    )

    channels: list[str] = DjangoModelRef(
        Subscription,
        "channels",
        default_factory=list,
    )

    class Meta:
        django_model_refs = {
            Subscription: [
                "identifier",
                "callback_url",
                "client_id",
                "secret",
            ]
        }
        extra_kwargs = {
            "identifier": {"examples": ["open-zaak"]},
            "callback_url": {"examples": ["https://example.com/api/webhook/"]},
            "client_id": {"examples": ["open-notificaties"]},
            "secret": {"examples": ["modify-this"]},
        }


class SubscriptionConfigurationModel(ConfigurationModel):
    items: list[SubscriptionConfigurationItem]
