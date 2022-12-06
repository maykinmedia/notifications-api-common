from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel
from zds_client import Client, ClientAuth
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from .query import NotificationsConfigManager


class NotificationsConfig(SingletonModel):
    notifications_api_service = models.ForeignKey(
        Service,
        limit_choices_to={"api_type": APITypes.nrc},
        verbose_name=_("notifications api service"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    notification_delivery_max_retries = models.PositiveIntegerField(
        help_text=_(
            "The maximum number of automatic retries. After this amount of retries, "
            "guaranteed delivery stops trying to deliver the message."
        ),
        default=5,
    )
    notification_delivery_retry_backoff = models.PositiveIntegerField(
        help_text=_(
            "If specified, a factor applied to the exponential backoff. "
            "This allows you to tune how quickly automatic retries are performed."
        ),
        default=3,
    )
    notification_delivery_retry_backoff_max = models.PositiveIntegerField(
        help_text=_("An upper limit in seconds to the exponential backoff time."),
        default=48,
    )

    objects = NotificationsConfigManager()

    class Meta:
        verbose_name = _("Notificatiescomponentconfiguratie")

    def __str__(self):
        api_root = (
            self.notifications_api_service.api_root
            if self.notifications_api_service
            else _("no service configured")
        )
        return _("Notifications API configuration ({api_root})").format(
            api_root=api_root
        )

    @classmethod
    def get_client(cls) -> Optional[Client]:
        """
        Construct a client, prepared with the required auth.
        """
        config = cls.get_solo()
        if config.notifications_api_service:
            return config.notifications_api_service.build_client()
        return None


class Subscription(models.Model):
    """
    A single subscription.

    TODO: on change/update, update the subscription
    """

    callback_url = models.URLField(
        _("callback url"), help_text=_("Where to send the notifications (webhook url)")
    )
    client_id = models.CharField(
        _("client ID"),
        max_length=50,
        help_text=_("Client ID to construct the auth token"),
    )
    secret = models.CharField(
        _("client secret"),
        max_length=50,
        help_text=_("Secret to construct the auth token"),
    )
    channels = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_("channels"),
        help_text=_("Comma-separated list of channels to subscribe to"),
    )

    _subscription = models.URLField(
        _("NC subscription"),
        blank=True,
        editable=False,
        help_text=_("Subscription as it is known in the NC"),
    )

    class Meta:
        verbose_name = _("Webhook subscription")
        verbose_name_plural = _("Webhook subscriptions")

    def __str__(self):
        return f"{', '.join(self.channels)} - {self.callback_url}"

    def register(self) -> None:
        """
        Registers the webhook with the notification component.
        """
        assert (
            NotificationsConfig.get_solo().notifications_api_service
        ), "No service for Notifications API configured"

        client = NotificationsConfig.get_client()

        # This authentication is for the NC to call us. Thus, it's *not* for
        # calling the NC to create a subscription.
        # TODO should be replaced with `TokenAuth`
        # see: maykinmedia/notifications-api-common/pull/1#discussion_r941450384
        self_auth = ClientAuth(
            client_id=self.client_id,
            secret=self.secret,
        )
        data = {
            "callbackUrl": self.callback_url,
            "auth": self_auth.credentials()["Authorization"],
            "kanalen": [
                {
                    "naam": channel,
                    # FIXME: You need to be able to configure these.
                    "filters": {},
                }
                for channel in self.channels
            ],
        }

        # register the subscriber
        subscriber = client.create("abonnement", data=data)

        self._subscription = subscriber["url"]
        self.save(update_fields=["_subscription"])
