=========
Changelog
=========

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
