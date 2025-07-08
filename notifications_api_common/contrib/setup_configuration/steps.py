import logging

from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed
from furl import furl
from zgw_consumers.models import Service

from notifications_api_common.models import NotificationsConfig, Subscription

from .models import NotificationConfigurationModel, SubscriptionConfigurationModel

logger = logging.getLogger(__name__)


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
        if model.notification_delivery_base_factor:
            config.notification_delivery_base_factor = (
                model.notification_delivery_base_factor
            )

        config.save()


class NotificationSubscriptionConfigurationStep(
    BaseConfigurationStep[SubscriptionConfigurationModel]
):
    """
    Configure settings for Notificaties API Subscriptions
    """

    verbose_name = "Configuration for Notificaties API Subscriptions"
    config_model = SubscriptionConfigurationModel
    namespace = "notifications_subscriptions_config"
    enable_setting = "notifications_subscriptions_config_enable"

    def execute(self, model: SubscriptionConfigurationModel):
        config = NotificationsConfig.get_solo()

        if not (notifications_api := config.notifications_api_service):
            raise ConfigurationRunFailed(
                "No Notifications API Service configured. Please ensure you've first "
                f"run {NotificationConfigurationStep.__name__}"
            )

        if len(model.items) == 0:
            raise ConfigurationRunFailed("You must configure at least one subscription")

        for item in model.items:
            detail_url = furl(notifications_api.api_root)
            detail_url.path /= f"/abonnement/{item.uuid!s}"
            detail_url.path.normalize()

            subscription, created = Subscription.objects.update_or_create(
                identifier=item.identifier,
                defaults={
                    "client_id": item.client_id,
                    "secret": item.secret,
                    "channels": item.channels,
                    "callback_url": item.callback_url,
                    "_subscription": str(detail_url),
                },
            )

            logger.debug(
                "%s subscription with identifier='%s' and pk='%s'",
                "Created" if created else "Updated",
                subscription.identifier,
                subscription.pk,
            )
