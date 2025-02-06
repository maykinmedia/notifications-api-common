Setup configuration
===================

Loading notification configuration from a YAML file
***************************************************

This library provides two ``ConfigurationStep`` implementations
(from the library ``django-setup-configuration``, see the
`documentation <https://github.com/maykinmedia/django-setup-configuration>`_
for more information on how to run ``setup_configuration``): one to configure the
service and retry settings, another to configure notification endpoint subscriptions.

To make use of this, you must install the ``setup-configuration`` dependency group:

.. code-block:: bash

    pip install zgw-consumers[setup-configuration]

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

.. setup-config-example:: notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep

.. setup-config-example:: notifications_api_common.contrib.setup_configuration.steps.NotificationSubscriptionConfigurationStep

Because ``notifications_api_service_identifier`` is required, it might also be useful
to use the `ServiceConfigurationStep <https://zgw-consumers.readthedocs.io/en/latest/setup_config.html>`_
from ``zgw-consumers`` to configure the ``Service`` object for the notifications API.

Note that the ``uuid`` field in your subscriptions config must point to an existing
``Abonnement`` in the Open Notificaties service configured through ``notifications_config``.
