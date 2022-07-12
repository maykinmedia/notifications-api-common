"""
Interface to get a zds_client object for a given URL.
"""
from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string

from zds_client import Client
from zgw_consumers.service import Service


def get_client(url: str, url_is_api_root=False) -> Optional[Client]:
    """
    Get a client instance for the given URL.

    If the setting CUSTOM_CLIENT_FETCHER is defined, then this callable is invoked.
    Otherwise we fall back on the default implementation.

    If no suitable client is found, ``None`` is returned.
    """
    custom_client_fetcher = getattr(settings, "CUSTOM_CLIENT_FETCHER", None)
    if custom_client_fetcher:
        client_getter = import_string(custom_client_fetcher)
        return client_getter(url)

    client = Service.get_client(url)

    return client
