Setup configuration
===================

Loading notification configuration from a YAML file
***************************************************

This library provides a ``ConfigurationStep``
(from the library ``django-setup-configuration``, see the
`documentation <https://github.com/maykinmedia/django-setup-configuration>`_
for more information on how to run ``setup_configuration``)
to configure the notification configuration.

To add this step to your configuration steps, add ``django_setup_configuration`` to ``INSTALLED_APPS`` and add the following setting:

    .. code:: python

        SETUP_CONFIGURATION_STEPS = [
            ...
            "notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep"
            ...
        ]

The YAML file that is passed to ``setup_configuration`` must set the
``notifications_config_enable`` flag to ``true`` to enable the step. All fields under ``notifications_config`` are optional.

Example file:

    .. code:: yaml

        notifications_config_enable: True
        notifications_config:
          notifications_api_service_identifier: notifs-api
          notification_delivery_max_retries: 1
          notification_delivery_retry_backoff: 2
          notification_delivery_retry_backoff_max: 3

If the ``notifications_api_service_identifier`` is specified, it might also be useful
to use the `ServiceConfigurationStep <https://zgw-consumers.readthedocs.io/en/latest/setup_config.html>`_
from ``zgw-consumers``.

