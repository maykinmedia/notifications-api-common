import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.urls import reverse

from ...kanalen import KANAAL_REGISTRY
from ...models import NotificationsConfig

logger = logging.getLogger(__name__)


class KanaalExists(Exception):
    pass


def create_kanaal(kanaal: str) -> None:
    """
    Create a kanaal, if it doesn't exist yet.
    """
    client = NotificationsConfig.get_client()

    # look up the exchange in the registry
    _kanaal = next(k for k in KANAAL_REGISTRY if k.label == kanaal)

    kanalen = client.list("kanaal", query_params={"naam": kanaal})
    if kanalen:
        raise KanaalExists()

    # build up own documentation URL
    domain = Site.objects.get_current().domain
    protocol = "https" if settings.IS_HTTPS else "http"
    documentation_url = (
        f"{protocol}://{domain}{reverse('notifications:kanalen')}#{kanaal}"
    )

    client.create(
        "kanaal",
        {
            "naam": kanaal,
            "documentatieLink": documentation_url,
            "filters": list(_kanaal.kenmerken),
        },
    )


class Command(BaseCommand):
    help = "Create kanaal in notification component"

    def add_arguments(self, parser):
        parser.add_argument("kanaal", nargs="?", type=str, help="Name of kanaal")

    def handle(self, **options):
        config = NotificationsConfig.get_solo()

        if not config.notifications_api_service:
            self.stderr.write(
                "NotificationsConfig does not have a `notifications_api_service` configured"
            )

        api_root = config.notifications_api_service.api_root

        # use CLI arg or fall back to setting
        kanaal = options["kanaal"] or settings.NOTIFICATIONS_KANAAL

        try:
            create_kanaal(kanaal)
            self.stdout.write(f"Registered kanaal '{kanaal}' with {api_root}")
        except KanaalExists:
            self.stderr.write(f"Kanaal '{kanaal}' already exists within {api_root}")
