from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from ape_pie.client import APIClient
from solo.models import SingletonModel
from zgw_consumers.client import ZGWAuth, build_client
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
        default=7,
    )
    notification_delivery_retry_backoff = models.PositiveIntegerField(
        help_text=_(
            "If specified, a factor applied to the exponential backoff. "
            "This allows you to tune how quickly automatic retries are performed."
        ),
        default=25,
    )
    notification_delivery_retry_backoff_max = models.PositiveIntegerField(
        help_text=_("An upper limit in seconds to the exponential backoff time."),
        default=52000,
    )
    notification_delivery_base_factor = models.PositiveIntegerField(
        help_text=_(
            "The base factor used for exponential backoff. "
            "This can be increased or decreased to spread retries over a longer or shorter time period."
        ),
        default=4,
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
    def get_client(cls) -> Optional[APIClient]:
        """
        Construct a client, prepared with the required auth.
        """
        config = cls.get_solo()
        if config.notifications_api_service:
            return build_client(
                config.notifications_api_service, client_factory=APIClient
            )
        return None


class Subscription(models.Model):
    """
    A single subscription.

    TODO: on change/update, update the subscription
    """

    identifier = models.SlugField(
        unique=True,
        blank=False,
        null=False,
        max_length=64,
        help_text=_("A human-friendly identifier to refer to this subscription."),
    )
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
        service = NotificationsConfig.get_solo().notifications_api_service
        assert service, "No service for Notifications API configured"

        client = NotificationsConfig.get_client()
        assert client

        # This authentication is for the NC to call us. Thus, it's *not* for
        # calling the NC to create a subscription.
        # TODO should be replaced with `TokenAuth`
        # see: maykinmedia/notifications-api-common/pull/1#discussion_r941450384
        self_auth = ZGWAuth(service)
        data = {
            "callbackUrl": self.callback_url,
            "auth": f"Bearer {self_auth._token}",
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
        subscriber = client.post("abonnement", json=data).json()

        self._subscription = subscriber["url"]
        self.save(update_fields=["_subscription"])
