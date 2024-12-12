Setup configuration
===================

Loading notification configuration from a YAML file
***************************************************

This library provides two ``ConfigurationStep`` implementations
(from the library ``django-setup-configuration``, see the
`documentation <https://github.com/maykinmedia/django-setup-configuration>`_
for more information on how to run ``setup_configuration``): one to configure the 
service and retry settings, another to configure notification endpoint subscriptions.

To add these steps to your configuration steps, add ``django_setup_configuration`` 
to ``INSTALLED_APPS`` and add the following settings:

    .. code:: python

        SETUP_CONFIGURATION_STEPS = [
            ...
            # Note the order: NotificationSubscriptionConfigurationStep expects a notification service
            # to have been configured by NotificationConfigurationStep
            "notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep"
            "notifications_api_common.contrib.setup_configuration.steps.NotificationSubscriptionConfigurationStep"
            ...
        ]

The YAML file that is passed to ``setup_configuration`` must set the appropriate 
flag and fields for both steps:

Example file:

    .. code:: yaml

        notifications_config_enable: True
        notifications_config:
          notifications_api_service_identifier: notifs-api
          notification_delivery_max_retries: 1
          notification_delivery_retry_backoff: 2
          notification_delivery_retry_backoff_max: 3

        notifications_subscriptions_config_enable: true
        notifications_subscriptions_config:
          items:
            - identifier: my-subscription
              callback_url: http://my/callback
              client_id: the-client
              secret: supersecret
              uuid: 0f616bfd-aacc-4d85-a140-2af17a56217b
              channels:
                - Foo
                - Bar

Because ``notifications_api_service_identifier`` is required, it might also be useful
to use the `ServiceConfigurationStep <https://zgw-consumers.readthedocs.io/en/latest/setup_config.html>`_
from ``zgw-consumers`` to configure the ``Service`` object for the notifications API.

Note that the ``uuid`` field in your subscriptions config must point to an existing
``Abonnement`` in the Open Notificaties service configured through ``notifications_config``.
