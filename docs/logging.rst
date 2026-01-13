Logging
=======

This library emits structured log events using ``structlog``. The consuming application
is responsible for log configuration and formatting.

This page documents the log ``events`` emitted by this library.

Notification events
-------------------

* ``notifications_client_unavailable``: could not construct a Notifications API client due to missing or invalid configuration.

* ``notification_delivery_failed``: sending a notification to the Notifications API failed with an HTTP error. Additional context: ``base_url``, ``notification_msg``, ``current_try``, ``final_try``.

* ``no_notification_source_set``: ``NOTIFICATIONS_SOURCE`` is not configured.

* ``cloudevent_delivery_failed``: sending a cloudevent failed with an HTTP error. Additional context: ``base_url``, ``cloudevent_msg``, ``current_try``, ``final_try``.

* ``notification_skipped_non_success_status``: a view returned a non-success HTTP status code. Additional context: ``status_code``.

* ``subscription_created_or_updated``: a Notifications API subscription was created or updated via configuration steps. Additional context: ``action`` (created/updated), ``identifier``, ``pk``.

* ``multiple_kanalen_found``: more than one kanaal with the same name was returned while running the `register_kanalen` command. Additional context: ``kanaal``, ``count``.
