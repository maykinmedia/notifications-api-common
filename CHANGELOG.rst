=========
Changelog
=========

0.5.0 (2024-12-20)
------------------

* Changes to ``Kanaal.get_kenmerken`` to:

    * support nested kenmerken
    * allow using the ``request`` parameter
    * specify custom help texts for kenmerken
* Add ``generate_notificaties`` management command (ported over from ``commonground-api-common``)
* Update existing kanalen when running the ``register_kanalen`` management command

0.4.0 (2024-12-12)
------------------

* Added an ``identifier`` field to the ``Subscription`` model
* Introduced support for ``django-setup-configuration`` and added two
  ``ConfigurationStep`` implementations: ``NotificationConfigurationStep`` and
  ``NotificationSubscriptionConfigurationStep``

0.3.1 (2024-10-27)
------------------

* Fixed kanalen not being registered. This regression was introduced in ``0.3.0``.

0.3.0 (2024-10-24)
------------------

* Upgraded Django requirement  to >= 4.2
* Upgraded minimum python requirement to >= 3.10
* Added python 3.12 support
* Added the ``NOTIFICATIONS_GUARANTEE_DELIVERY`` environment variable which allows
  ``RuntimeError`` to be raised (or not to) whenever no Notifications API is
  configured. The default for this setting is set to ``True``.
* Upgraded zgw-consumers to 0.35.1

    * This removed support for retrieving external OAS files to determine
    * This requires ``zgw_consumers.models.Service`` ("service") instances to be
      created to do external API calls through ``zgw_consumers``

0.2.2 (2023-04-20)
------------------

Fixed a crash in migrations during fresh installs when using the latest zgw-consumers.

0.2.1 (2023-02-07)
------------------

Fixed automatic retry for assured delivery introduced in 0.2.0

* After automatic retries are exhausted failed notifications with 50x HTTP statuses
  will be shown in the admin interface.

0.2.0 (2022-12-14)
------------------

Feature release for assured delivery.

The notification delivery mechanism is now delegated to Celery, so make sure to
configure celery correctly in your project and deploy (one or more) task workers in
your infrastructure. Autoretry behaviour can be configured in the admin interface.

Other changes:

* Added support for gemma-zds-client 2.0+
* Updated CI pipeline for deprecated actions
* Fixed some package metadata
* Removed deprecated Django < 3.2 constructs
* Added NL and EN translations

0.1.0 (2022-09-28)
------------------

Extracted the shared notification publishing/subscribing code from vng-api-common.

This includes some refactors where the service configuration now makes use of
zgw-consumers, breaking away from ``Secret``, ``APICredential`` and other config models
of vng-api-common.
