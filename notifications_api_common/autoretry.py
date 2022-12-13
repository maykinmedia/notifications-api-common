from celery.exceptions import Ignore, Retry
from celery.utils.time import get_exponential_backoff_interval
from vine.utils import wraps

from .models import NotificationsConfig


def add_autoretry_behaviour(task, **options):
    """
    Adapted from celery to use admin configurable autoretry settings
    celery original code: https://github.com/celery/celery/blob/master/celery/app/autoretry.py

    Why we implement it this way:
    autoretry in Celery is implemented using `add_autoretry_behaviour` which basically
    patches `task.run` method during task initialization.
    `add_autoretry_behaviour` evaluates all the autoretry properties which can be specified
    in @celery.task decorator or in the `Task` class. Either way they are specified and evaluated
    during task initialization, which happens only once for each task.

    That means, that it is impossible to add dynamic autoretry properties without changing
    `add_autoretry_behaviour` behaviour: even if we add descriptors or class properties
    they would be evaluated only once.

    The only solution to add dynamic properties is to patch `task.run` method, so it will evaluate
    autoretry options during calling of the task.

    The purpose of this long docstring is to share the pain and to warn future developers who would
    want to optimize autoretry implementation
    """
    autoretry_for = tuple(
        options.get("autoretry_for", getattr(task, "autoretry_for", ()))
    )
    retry_kwargs = options.get("retry_kwargs", getattr(task, "retry_kwargs", {}))
    retry_jitter = options.get("retry_jitter", getattr(task, "retry_jitter", True))

    if autoretry_for and not hasattr(task, "_orig_run"):

        @wraps(task.run)
        def run(*args, **kwargs):
            config = NotificationsConfig.get_solo()
            max_retries = config.notification_delivery_max_retries
            retry_backoff = config.notification_delivery_retry_backoff
            retry_backoff_max = config.notification_delivery_retry_backoff_max

            task.max_retries = max_retries

            try:
                return task._orig_run(*args, **kwargs)
            except Ignore:
                # If Ignore signal occurs task shouldn't be retried,
                # even if it suits autoretry_for list
                raise
            except Retry:
                raise
            except autoretry_for as exc:
                if retry_backoff:
                    retry_kwargs["countdown"] = get_exponential_backoff_interval(
                        factor=retry_backoff,
                        retries=task.request.retries,
                        maximum=retry_backoff_max,
                        full_jitter=retry_jitter,
                    )
                # Override max_retries
                if hasattr(task, "override_max_retries"):
                    retry_kwargs["max_retries"] = getattr(
                        task, "override_max_retries", max_retries
                    )

                ret = task.retry(exc=exc, **retry_kwargs)
                # Stop propagation
                if hasattr(task, "override_max_retries"):
                    delattr(task, "override_max_retries")
                raise ret

        task._orig_run, task.run = task.run, run
