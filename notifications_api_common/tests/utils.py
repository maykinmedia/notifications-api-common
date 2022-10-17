from threading import Thread

from django.db import transaction

from notifications_api_common.viewsets import NotificationMixin


def mock_notify(*args, **kwargs) -> None:
    def _send():
        NotificationMixin.send_notification(*args, **kwargs)

    transaction.on_commit(_send)


def mock_notify_async(*args, **kwargs) -> None:
    def _send():
        NotificationMixin.send_notification(*args, **kwargs)

    thread = Thread(target=_send)
    thread.start()
    thread.join()
