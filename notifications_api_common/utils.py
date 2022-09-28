from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.urls import Resolver404, ResolverMatch, get_resolver, get_script_prefix

from rest_framework.viewsets import ViewSet

from .kanalen import Kanaal


def notification_documentation(kanaal: Kanaal):
    """
    Generate notification documentation for an OpenAPI specification containing
    the relevant resources and actions for a given KANAAL
    """
    doc = f"""Deze API publiceert notificaties op het kanaal `{kanaal.label}`.

{kanaal.description}

**Resources en acties**
"""
    for resource, actions in kanaal.get_usage():
        doc += f"""- `{resource}`: {', '.join(actions)}\n"""
    return doc


class NotAViewSet(Exception):
    pass


def resolve_path(path: str, resolver=None, script_prefix=None) -> ResolverMatch:
    resolver = resolver or get_resolver()
    prefix = script_prefix or get_script_prefix()
    path = path.replace(prefix, "/", 1)
    try:
        return resolver.resolve(path)
    except Resolver404 as exc:
        raise models.ObjectDoesNotExist("URL did not resolve") from exc


def get_viewset_for_path(path: str, method="GET") -> "ViewSet":
    """
    Look up which viewset matches a path.
    """
    # NOTE: this doesn't support setting a different urlconf on the request
    callback, callback_args, callback_kwargs = resolve_path(path)

    if not hasattr(callback, "cls"):
        raise NotAViewSet(f"Callback for {path} does not look like a viewset")

    viewset = callback.cls(**callback.initkwargs)
    viewset.action_map = callback.actions
    viewset.request = HttpRequest()
    viewset.args = callback_args
    viewset.kwargs = callback_kwargs

    viewset.action = viewset.action_map.get(method.lower())

    return viewset


def get_resource_for_path(path: str) -> models.Model:
    """
    Retrieve the API instance belonging to a (detail) path.
    """
    if settings.FORCE_SCRIPT_NAME and path.startswith(settings.FORCE_SCRIPT_NAME):
        prefix_length = len(settings.FORCE_SCRIPT_NAME)
        path = path[prefix_length:]

    viewset = get_viewset_for_path(path)

    # See rest_framework.mixins.RetieveModelMixin.get_object()
    lookup_url_kwarg = viewset.lookup_url_kwarg or viewset.lookup_field
    filter_kwargs = {viewset.lookup_field: viewset.kwargs[lookup_url_kwarg]}

    return viewset.get_queryset().get(**filter_kwargs)
