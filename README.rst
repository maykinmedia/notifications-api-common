notifications-api-common
========================

:Version: 0.8.1
:Source: https://github.com/maykinmedia/notifications-api-common
:Keywords: notifications, REST, API, Common Ground, ZGW
:PythonVersion: 3.12

|build-status| |code-quality| |ruff| |coverage| |docs|

|python-versions| |django-versions| |pypi-version|

Re-usable integration layer for the Common Ground Notifications API specification.

.. contents::

.. section-numbering::

Features
========

* Define your own notifications channels
* Easily emit notifications from your API endpoints (using DRF)
* Manage subscriptions to receive notifications

Installation
============

Requirements
------------

* Python 3.10 or above
* setuptools 30.3.0 or above
* Django 4.2 or newer
* Celery 5.0 or newer setup with one worker deployed


Install
-------

.. code-block:: bash

    pip install notifications-api-common


Usage
=====

See the `documentation <https://notifications-api-common.readthedocs.io/>`_.


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
