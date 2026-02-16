"""
Provide notifications kanaal/exchange classes.
"""

from collections import defaultdict
from typing import Any, Dict, Literal, Tuple, Type, cast

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models import Field, Model

from rest_framework.request import Request

KANAAL_REGISTRY = set()


class Kanaal:
    def __init__(
        self,
        label: str,
        main_resource: Type[Model],
        kenmerken: Tuple | None = None,
        extra_kwargs: dict[str, dict[Literal["help_text"], str]] | None = None,
    ):
        self.label = label
        self.main_resource = main_resource
        self.extra_kwargs = extra_kwargs or {}

        self.usage = defaultdict(list)  # filled in by metaclass of notifications

        # check that we're refering to existing fields
        self.kenmerken = kenmerken or ()
        for kenmerk in self.kenmerken:
            try:
                self.get_field(self.main_resource, kenmerk)
            except FieldDoesNotExist as exc:
                model_name = cast(Any, main_resource)._meta.model_name
                raise ImproperlyConfigured(
                    f"Kenmerk '{kenmerk}' does not exist on the model {model_name}"
                ) from exc

        KANAAL_REGISTRY.add(self)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "%s(label=%r, main_resource=%r)" % (
            cls_name,
            self.label,
            self.main_resource,
        )

    @staticmethod
    def get_field(model: Type[Model], field_name: str) -> Field:
        """
        Function to retrieve a field from a Model
        """
        return cast(Field, cast(Any, model)._meta.get_field(field_name))

    def get_help_text(self, field: Field, kenmerk: str) -> str:
        """
        Retrieve the help_text for a kenmerk, pulled from the model field by default,
        but can be overridden by setting extra_kwargs on `Kanaal.__init__`
        """
        if help_text := self.extra_kwargs.get(kenmerk, {}).get("help_text"):
            return help_text
        return str(field.help_text)

    def get_kenmerken(
        self,
        obj: Model,
        data: dict | None = None,
        request: Request | None = None,  # noqa
    ) -> Dict:
        data = data or {}
        return {
            kenmerk: data.get(kenmerk, getattr(obj, kenmerk))
            for kenmerk in self.kenmerken
        }

    def get_usage(self):
        return self.usage.items()

    @property
    def description(self) -> str:
        kenmerk_template = "* `{kenmerk}`: {help_text}"
        kenmerken = [
            kenmerk_template.format(
                kenmerk=kenmerk,
                help_text=self.get_help_text(
                    self.get_field(self.main_resource, kenmerk), kenmerk
                ),
            )
            for kenmerk in self.kenmerken
        ]

        options = cast(Any, self.main_resource)._meta

        kenmerken_str = "\n".join(kenmerken)

        return (
            "**Main resource**\n\n"
            f"`{options.model_name}`\n\n\n\n"
            "**Kenmerken**\n\n"
            f"{kenmerken_str}"
        )
