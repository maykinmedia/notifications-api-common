import logging
from typing import Optional

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.urls import reverse

from requests import Response
from requests.exceptions import JSONDecodeError, RequestException
from zgw_consumers.models import Service

from ...kanalen import KANAAL_REGISTRY
from ...models import NotificationsConfig
from ...settings import get_setting

logger = logging.getLogger(__name__)


class KanaalException(Exception):
    kanaal: str
    data: dict | list
    service: Service

    def __init__(
        self, kanaal: str, service: Service, data: Optional[dict | list] = None
    ):
        super().__init__()

        self.kanaal = kanaal
        self.service = service
        self.data = data or {}


class KanaalRequestException(KanaalException):
    def __str__(self) -> str:
        return (
            f"Unable to retrieve kanaal {self.kanaal} from {self.service}: {self.data}"
        )


class KanaalCreateException(KanaalException):
    def __str__(self) -> str:
        return f"Unable to create kanaal {self.kanaal} at {self.service}: {self.data}"


class KanaalExistsException(KanaalException):
    def __str__(self) -> str:
        return f"Kanaal '{self.kanaal}' already exists within {self.service}"


def create_kanaal(kanaal: str, service: Service) -> None:
    """
    Create a kanaal, if it doesn't exist yet.
    """
    client = NotificationsConfig.get_client()

    assert client

    # look up the exchange in the registry
    _kanaal = next(k for k in KANAAL_REGISTRY if k.label == kanaal)

    response_data = []

    try:
        response: Response = client.get("kanaal", params={"naam": kanaal})
        kanalen: list[dict] = response.json() or []
        response.raise_for_status()
    except (RequestException, JSONDecodeError) as exception:
        raise KanaalRequestException(
            kanaal=kanaal, service=service, data=response_data
        ) from exception

    if kanalen:
        raise KanaalExistsException(kanaal=kanaal, service=service, data=response_data)

    # build up own documentation URL
    domain = Site.objects.get_current().domain
    protocol = "https" if get_setting("IS_HTTPS") else "http"
    documentation_url = (
        f"{protocol}://{domain}{reverse('notifications:kanalen')}#{kanaal}"
    )

    try:
        response: Response = client.post(
            "kanaal",
            json={
                "naam": kanaal,
                "documentatieLink": documentation_url,
                "filters": list(_kanaal.kenmerken),
            },
        )

        response_data: dict = response.json() or {}
        response.raise_for_status()
    except (RequestException, JSONDecodeError) as exception:
        raise KanaalCreateException(
            kanaal=kanaal, service=service, data=response_data
        ) from exception


class Command(BaseCommand):
    help = "Create kanaal in notification component"

    def add_arguments(self, parser):
        parser.add_argument(
            "--kanalen",
            nargs="*",
            type=str,
            help=(
                "Names of the kanalen (will use the `KANAAL_REGISTRY` if not specified)"
            ),
        )

    def handle(self, **options):
        config = NotificationsConfig.get_solo()

        if not config.notifications_api_service:
            self.stderr.write(
                "NotificationsConfig does not have a "
                "`notifications_api_service` configured"
            )

        service = config.notifications_api_service

        # use CLI arg or fall back to setting
        kanalen = options["kanalen"] or sorted(
            [kanaal.label for kanaal in KANAAL_REGISTRY]
        )

        for kanaal in kanalen:
            try:
                create_kanaal(kanaal, service)
                self.stdout.write(
                    f"Registered kanaal '{kanaal}' with {service.api_root}"
                )
            except (KanaalException,) as exception:
                self.stderr.write(f"{str(exception)} . Skipping..")
