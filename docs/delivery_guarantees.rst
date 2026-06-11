.. _delivery_guarantees:

Delivery guarantees
===================

Mechanism
---------

The Notificaties API standard (and by extension notifications_api_common) operates on a simple
yet powerful message delivery mechanism: webhooks_.

A webhook, in essence, is nothing more than and HTTP endpoint exposed by a server where
HTTP requests/messages can be sent to. Upon receiving such a request, the webhook
receiver is responsible for processing the content of this request appropriately.

Webhooks are registered by parties interested in receiving notifications. The webhook
registration is recorded and saved in Open Notificaties. Whenever (another) party
publishes a notification, it does so by making a ``HTTP POST`` call to the Open
Notificaties API. Open Notificaties, in turn, checks which parties should receive this
notification and forwards the message to the registered webhook.

.. _webhooks: https://en.wikipedia.org/wiki/Webhook

Failure modes
-------------

Even though the mechanism is simple, the underlying infrastructure is not. There is
always a chance that a message does not get properly delivered - a problem that all
*message broker* systems have.

The Notificaties API standard defines that recipients of a message/notification have to
reply with a HTTP 204 status code to confirm that the message was received. However,
to complicate things further, this confirmation response may also be lost. To summarize,
the following scenarios are possible:

* notifications_api_common delivers message and receives confirmation (happy flow)
* notifications_api_common delivers message but does not receive a confirmation (failure mode)
* notifications_api_common fails to deliver the message successfully (failure mode)

Now there are essentially two mitigation modes available:

* at-most-once delivery
* at-least-once delivery

Delivering a message exactly once is not possible since the underlying infrastructure
("the internet") may fail for whatever reason.


Retry mechanism
~~~~~~~~~~~~~~~

By default, sending notifications to Open Notificaties has automatic retry behaviour, i.e. if the notification
task has failed, it will automatically be rescheduled/tried again until the maximum
retry limit has been reached.

Autoretry explanation and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retry behaviour is implemented using binary exponential backoff with a delay factor,
the formula to calculate the time to wait until the next retry is as follows:

.. math::
    t = \text{backoff\_factor} * \text{base\_factor}^c

where `t` is time in seconds and  `c` is the number of retries that have been performed already.

This behaviour can be configured using :ref:`setup_config`
and also via the admin interface at **Configuratie > Notificatiescomponentconfiguratie**:

* **Notification delivery max retries**: the maximum number of retries the task queue
  will do if sending a notification has failed. Default is ``7``.
* **Notification delivery retry backoff**: a boolean or a number. If this option is set to
  ``True``, autoretries will be delayed following the rules of binary exponential backoff. If
  this option is set to a number, it is used as a delay factor. Default is ``25``.
* **Notification delivery retry backoff max**: an integer, specifying number of seconds.
  If ``Notification delivery retry backoff`` is enabled, this option will set a maximum
  delay in seconds between task autoretries. Default is ``52000`` seconds.
* **Notification delivery base factor**: the base factor used for exponential backoff.
  This can be increased or decreased to spread retries over a longer or shorter time period.
  Default is ``4``.

With the assumption that the requests are done immediately we can model the notification
tasks schedule with the default configurations:

1. At 0s the request to send a Notification to a subscriber is made, the notification task is scheduled, picked up
   by worker and failed
2. At 25s with 25s delay the first retry happens (``4^0`` * ``Notification delivery retry backoff``)
3. At 2m5s with 100s delay - the second retry (``4^1`` * ``Notification delivery retry backoff``)
4. At 8m45s with 400s delay - the third retry
5. At 35m25s with 1600s delay - the fourth retry
6. At 2h22m5s with 6400s delay - the fifth retry
7. At 9h28m45s with 25600s delay - the sixth retry
8. At 23h55m25s with 52000s delay - the seventh and final retry, capped by max delay.

So if the subscribed webhooks is up after 1 min of downtime the default configuration can handle it
automatically.



LOG_NOTIFICATIONS_IN_DB
~~~~~~~~~~~~~~~~~~~~~~~
When ``LOG_NOTIFICATIONS_IN_DB`` is set to ``True``, failed notifications are stored in the database with all their failed requests.
From the admin they can be manually restarted. The Notification will be deleted on a successful request.

With the command ``clean_failed_notifications`` all notifications older than ``NOTIFICATION_NUMBER_OF_DAYS_RETAINED`` (default 60 days) can be removed.