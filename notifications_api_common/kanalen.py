"""
Provide notifications kanaal/exchange classes.
"""

from collections import defaultdict
from typing import Dict, Tuple, Union

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models import Field, Model

from rest_framework.request import Request

KANAAL_REGISTRY = set()


class Kanaal:
    def __init__(
        self, label: str, main_resource: Model, kenmerken: Union[Tuple, None] = None
    ):
        self.label = label
        self.main_resource = main_resource

        self.usage = defaultdict(list)  # filled in by metaclass of notifications

        # check that we're refering to existing fields
        self.kenmerken = kenmerken or ()
        for kenmerk in self.kenmerken:
            try:
                self._get_field(self.main_resource, kenmerk)
            except FieldDoesNotExist as exc:
                raise ImproperlyConfigured(
                    f"Kenmerk '{kenmerk}' does not exist on the model {main_resource}"
                ) from exc

        KANAAL_REGISTRY.add(self)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "%s(label=%r, main_resource=%r)" % (
            cls_name,
            self.label,
            self.main_resource,
        )

    def _get_field(self, model: Model, field: str) -> Field:
        """
        Function to retrieve a field from a Model
        """
        return model._meta.get_field(field)

    def get_kenmerken(
        self,
        obj: Model,
        data: Union[Dict, None] = None,
        request: Union[Request, None] = None,  # noqa
    ) -> Dict:
        data = data or {}
        return {
            kenmerk: data.get(kenmerk, getattr(obj, kenmerk))
            for kenmerk in self.kenmerken
        }

    def get_usage(self):
        return self.usage.items()

    @property
    def description(self):
        kenmerk_template = "* `{kenmerk}`: {help_text}"
        kenmerken = [
            kenmerk_template.format(
                kenmerk=kenmerk,
                help_text=self._get_field(self.main_resource, kenmerk).help_text,
            )
            for kenmerk in self.kenmerken
        ]

        description = (
            "**Main resource**\n\n"
            "`{options.model_name}`\n\n\n\n"
            "**Kenmerken**\n\n"
            "{kenmerken}"
        ).format(options=self.main_resource._meta, kenmerken="\n".join(kenmerken))

        return description
