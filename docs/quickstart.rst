==========
Quickstart
==========

Installation
============

Pre-requisites
--------------

* Python 3.7 or higher
* Setuptools 30.3.0 or higher
* Only the PostgreSQL database is supported

Install from PyPI
-----------------

Install from PyPI with pip:

.. code-block:: bash

    pip install notifications-api-common

This library ships with support for notifications, in the form of view(set)
mixins and some simple configuration data models.

Installation
------------

Add the following apps

.. code-block:: python

    ...,
    'django.contrib.sites',
    'notifications_api_common',
    'rest_framework',
    'solo',
    'zgw_consumers',
    ...

to your ``INSTALLED_APPS`` setting.

Three additional settings are available:

* ``NOTIFICATIONS_KANAAL``: a string, the label of the 'kanaal' to register
  with the NC
* ``NOTIFICATIONS_DISABLED``: a boolean, default ``False``. Set to ``True`` to
  completely disable the sending of notifications.
* ``IS_HTTPS``: a boolean, default ``False``. Set to ``True`` to indicate that HTTPS is being used
* ``NOTIFICATIONS_KANALEN_TEMPLATE``: a string. Set this to a path that contains a template to use for the ``KanalenView``

Make sure to migrate your database:

.. code-block:: bash

    python manage.py migrate

Configuration
-------------

In the admin interface, open the notifications configuration and create a ``Service``
for the NC to use.

Make sure you also have the ``Sites`` set up correctly, as the domain
configured there is used to build the documentation URL.

After entering the configuration, you can register your 'kanaal' - this action
is idempotent:

.. code-block:: bash

    python manage.py register_kanalen

**Usage in code**

Define at least one ``Kanaal`` instance, typically this would go in
``api/kanalen.py``:

.. code-block:: python

    from notifications_api_common.kanalen import Kanaal

    from zrc.datamodel.models import Zaak

    ZAKEN = Kanaal(
        'zaken',  # label of the channel/exchange
        main_resource=Zaak,  # main object for this channel/exchange
        kenmerken=(  # fields to include as 'kenmerken'
            'bronorganisatie',
            'zaaktype',
            'vertrouwelijkheidaanduiding'
        )
    )

To send notifications, add the mixins to the viewsets:

* ``notifications_api_common.viewsets.NotificationCreateMixin``:
  send notifications for newly created objects

* ``notifications_api_common.viewsets.NotificationUpdateMixin``:
  send notifications for (partial) upates to objects

* ``notifications_api_common.viewsets.NotificationDestroyMixin``:
  send notifications for destroyed objects

* ``notifications_api_common.viewsets.NotificationViewSetMixin``:
  a combination of all three mixins above

and define the attribute ``notifications_kanaal`` on the viewset:

.. code-block:: python

    from .kanalen import ZAKEN


    class ZaakViewSet(NotificationViewSetMixin, viewsets.ModelViewSet):
        ...
        notifications_kanaal = ZAKEN
