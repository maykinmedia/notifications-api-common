from notifications_api_common.viewsets import NotificationMixin
from django.db import transaction


def mock_notify(*args, **kwargs) -> None:
    def _send():
        NotificationMixin.send_notification(*args, **kwargs)

    transaction.on_commit(_send)
