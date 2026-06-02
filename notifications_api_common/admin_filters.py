from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BaseFilter(admin.SimpleListFilter):
    title = None
    parameter_name = None
    field_name = None

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        choices = qs.values_list(self.field_name, flat=True).distinct()
        return (
            (
                choice,
                choice,
            )
            for choice in choices
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return queryset.filter(**{self.field_name: self.value()})


class ActionFilter(BaseFilter):
    title = _("action")
    parameter_name = "actie"
    field_name = "message__actie"


class ResourceFilter(BaseFilter):
    title = _("resource")
    parameter_name = "resource"
    field_name = "message__resource"
