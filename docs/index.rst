.. notifications_api_common documentation main file, created by startproject.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

notifications-api-common
========================

|build-status| |code-quality| |ruff| |coverage| |docs|

|python-versions| |django-versions| |pypi-version|

Re-usable integration layer for the Common Ground Notifications API specification.

Features
========

* Define your own notifications channels
* Easily emit notifications from your API endpoints (using DRF)
* Manage subscriptions to receive notifications

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   setup_config
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |build-status| image:: https://github.com/maykinmedia/notifications-api-common/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/notifications-api-common/actions?query=workflow%3A%22Run+CI%22

.. |code-quality| image:: https://github.com/maykinmedia/notifications-api-common/workflows/Code%20quality%20checks/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/notifications-api-common/actions?query=workflow%3A%22Code+quality+checks%22

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |coverage| image:: https://codecov.io/gh/maykinmedia/notifications-api-common/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/notifications-api-common
    :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/notifications-api-common/badge/?version=latest
    :target: https://notifications-api-common.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/notifications-api-common.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/notifications-api-common.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/notifications-api-common.svg
    :target: https://pypi.org/project/notifications-api-common/
