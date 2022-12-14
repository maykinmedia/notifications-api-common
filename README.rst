notifications-api-common
========================

:Version: 0.2.0
:Source: https://github.com/maykinmedia/notifications-api-common
:Keywords: notifications, REST, API, Common Ground, ZGW
:PythonVersion: 3.9

|build-status| |code-quality| |black| |coverage| |docs|

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

* Python 3.7 or above
* setuptools 30.3.0 or above
* Django 3.2 or newer


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

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

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
