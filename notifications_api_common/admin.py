from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from requests.exceptions import RequestException
from solo.admin import SingletonModelAdmin

from .models import NotificationsConfig, Subscription


@admin.register(NotificationsConfig)
class NotificationsConfigAdmin(SingletonModelAdmin):
    pass


def register_webhook(modeladmin, request, queryset):
    for sub in queryset:
        if sub._subscription:
            continue

        try:
            sub.register()
        except RequestException as e:
            messages.error(
                request,
                _(
                    "Something went wrong while registering subscription "
                    "for {callback}: {exception}"
                ).format(callback=sub.callback_url, exception=e),
            )


register_webhook.short_description = _("Register the webhooks")  # noqa


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("callback_url", "channels", "_subscription")
    actions = [register_webhook]
