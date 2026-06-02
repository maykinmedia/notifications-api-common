from django.contrib import admin, messages
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from requests.exceptions import RequestException
from solo.admin import SingletonModelAdmin

from notifications_api_common.admin_filters import ActionFilter, ResourceFilter
from notifications_api_common.tasks import send_cloudevent, send_notification

from .models import (
    Notification,
    NotificationResponse,
    NotificationsConfig,
    NotificationTypes,
    Subscription,
)


@admin.register(NotificationsConfig)
class NotificationsConfigAdmin(SingletonModelAdmin):
    pass


@admin.action(description=_("Register the webhooks"))
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("identifier", "callback_url", "channels", "_subscription")
    actions = [register_webhook]


class NotificationResponseInline(admin.TabularInline):
    model = NotificationResponse


def _send(notification: Notification):
    match notification.type:
        case NotificationTypes.notification:
            assert hasattr(send_notification, "_orig_run")
            send_notification.delay(notification.message, notification.id)  # pyright: ignore
        case NotificationTypes.cloudevent:
            send_cloudevent.delay(notification.message, notification.id)  # pyright: ignore


@admin.action(description=_("Re-send the selected notifications to all subscriptions"))
def resend_notifications(modeladmin, request, queryset):
    # Save all the selected notifications via the modeladmin, triggering
    # the notification mechanism
    for notification in queryset:
        _send(notification)

    messages.add_message(
        request, messages.SUCCESS, _("Selected notifications have been scheduled.")
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "action",
        "resource",
    )
    inlines = (NotificationResponseInline,)
    actions = [resend_notifications]

    list_filter = (
        ActionFilter,
        ResourceFilter,
    )
    search_fields = ("message",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(failed_responses_count=Count("notificationresponse"))
        return qs

    @admin.display(description=_("Action"))
    def action(self, obj):
        return obj.message.get("actie")

    @admin.display(description=_("Resource"))
    def resource(self, obj):
        return obj.message.get("resource")

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        super().save_model(request, obj, form, change)

        _send(obj)
