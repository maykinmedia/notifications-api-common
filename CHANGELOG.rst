=========
Changelog
=========

0.8.0 (2025-07-08)
------------------

**New features**

* [open-zaak/open-notificaties#290] Add configurable base factor for retry mechanism,
  this is also configurable via ``setup_configuration`` via the attribute ``notification_delivery_base_factor`` (default: 4)
* Modify defaults for retry behavior:

  * ``notification_delivery_max_retries`` to 7
  * ``notification_delivery_retry_backoff`` to 25
  * ``notification_delivery_retry_backoff_max`` to 52000

**Maintenance**

* Replace ``bumpversion`` with ``bump-my-version``

0.7.3 (2025-06-17)
------------------

**New features**

* [#37] Set the ``notifications_api_service_identifier`` field as required in setup-configuration
* Add the env variable ``TIME_LEEWAY`` that defines a leeway in ``UntilNowValidator``

**Maintenance**

* [maykinmedia/open-api-framework#132] Replace ``check_sphinx.py`` with ``make``
* [maykinmedia/open-api-framework#133] Replace ``black``, ``isort`` and ``flake8`` with ``ruff`` and update code-quality workflow
* [maykinmedia/open-api-framework#140] Upgrade python to 3.12

0.7.2 (2025-03-28)
------------------

* Add get_domain() for ``register_kanalen``

0.7.1 (2025-03-20)
------------------

* Fix quickstart.rst and add ``example.com`` as default value for SITE_DOMAIN

0.7.0 (2025-03-18)
------------------

* [#31] Add ``notificaties.md`` in manifest to make sure ``src/manage.py generate_notificaties`` works
* Fix incorrect kanaal name anchors on kanalen page
* [#59] Remove ``django.contrib.sites`` dependency and add ``SITE_DOMAIN`` environment variable

  .. warning::

      The ``SITE_DOMAIN`` must be configured to the correct domain to ensure ``src/manage.py register_kanalen`` works
      (e.g. if your application is hosted at ``application.local``, ``SITE_DOMAIN=application.local``)

0.6.0 (2025-02-06)
------------------

* Update setup-config docs to use example directive and add extra example values to models

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
