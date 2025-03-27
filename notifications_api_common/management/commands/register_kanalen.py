import logging
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from ape_pie.client import APIClient
from requests import Response
from requests.exceptions import JSONDecodeError, RequestException

from ...kanalen import KANAAL_REGISTRY
from ...models import NotificationsConfig
from ...settings import get_setting
from ...utils import get_domain

logger = logging.getLogger(__name__)


class KanaalException(Exception):
    kanaal: str
    data: dict | list
    base_url: str

    def __init__(self, kanaal: str, base_url: str, data: Optional[dict | list] = None):
        super().__init__()

        self.kanaal = kanaal
        self.base_url = base_url
        self.data = data or {}


class KanaalRequestException(KanaalException):
    def __str__(self) -> str:
        return (
            f"Unable to retrieve kanaal {self.kanaal} from {self.base_url}: {self.data}"
        )


class KanaalCreateException(KanaalException):
    def __str__(self) -> str:
        return f"Unable to create kanaal {self.kanaal} at {self.base_url}: {self.data}"


class KanaalUpdateException(KanaalException):
    def __str__(self) -> str:
        return f"Unable to update kanaal {self.kanaal} at {self.base_url}: {self.data}"


class KanaalExistsException(KanaalException):
    def __str__(self) -> str:
        return f"Kanaal '{self.kanaal}' already exists within {self.base_url}"


def get_kanaal(kanaal: str, client: APIClient) -> dict | None:
    response_data = []

    try:
        response: Response = client.get("kanaal", params={"naam": kanaal})
        kanalen: list = response.json()
        response.raise_for_status()
    except (RequestException, JSONDecodeError) as exception:
        raise KanaalRequestException(
            kanaal=kanaal, base_url=client.base_url, data=response_data
        ) from exception
    else:
        if kanalen:
            # `Kanaal.naam` is unique in Open Notificaties, so there should only be one
            if len(kanalen) > 1:
                logger.error(
                    "Found more than one Kanaal with naam %s, this should not be possible",
                    kanaal,
                )
            return kanalen[0]
        return None


def construct_kanaal_request_data(kanaal: str):
    _kanaal = next(k for k in KANAAL_REGISTRY if k.label == kanaal)

    # build up own documentation URL
    domain = get_domain()
    protocol = "https" if get_setting("IS_HTTPS") else "http"
    documentation_url = (
        f"{protocol}://{domain}{reverse('notifications:kanalen')}#{kanaal}"
    )

    data = {
        "naam": kanaal,
        "documentatieLink": documentation_url,
        "filters": list(_kanaal.kenmerken),
    }
    return data


def create_kanaal(kanaal: str, client) -> None:
    """
    Create a kanaal, if it doesn't exist yet.
    """
    data = construct_kanaal_request_data(kanaal)

    response_data = {}
    try:
        response: Response = client.post("kanaal", json=data)

        response_data: dict = response.json()
        response.raise_for_status()
    except (RequestException, JSONDecodeError) as exception:
        raise KanaalCreateException(
            kanaal=kanaal, base_url=client.base_url, data=response_data
        ) from exception


def replace_kanaal(kanaal: str, existing_kanaal: dict, client: APIClient) -> None:
    """
    Fully update a kanaal, if it doesn't exist yet.
    """
    data = construct_kanaal_request_data(kanaal)

    response_data = {}
    try:
        response: Response = client.put(existing_kanaal["url"], json=data)
        response_data: dict = response.json()
        response.raise_for_status()
    except (RequestException, JSONDecodeError) as exception:
        raise KanaalUpdateException(
            kanaal=kanaal, base_url=client.base_url, data=response_data
        ) from exception
    return


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
            raise CommandError(
                "NotificationsConfig does not have a "
                "`notifications_api_service` configured"
            )

        # use CLI arg or fall back to setting
        kanalen = options["kanalen"] or sorted(
            [kanaal.label for kanaal in KANAAL_REGISTRY]
        )

        client = NotificationsConfig.get_client()
        assert client

        for kanaal in kanalen:
            try:
                if existing_kanaal := get_kanaal(kanaal, client):
                    replace_kanaal(kanaal, existing_kanaal, client)
                    self.stdout.write(
                        f"Updated already existing kanaal '{kanaal}' with {client.base_url}"
                    )
                else:
                    create_kanaal(kanaal, client)
                    self.stdout.write(
                        f"Registered kanaal '{kanaal}' with {client.base_url}"
                    )
            except (KanaalException,) as exception:
                self.stderr.write(f"{str(exception)} . Skipping..")
