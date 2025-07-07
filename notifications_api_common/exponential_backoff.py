import random


def get_exponential_backoff_interval(
    factor: int, retries: int, maximum: int, base: int, full_jitter: bool = False
) -> int:
    """
    Calculate the exponential backoff wait time.

    This function is taken from Celery but overridden here to make sure the base factor is configurable.
    (https://docs.celeryq.dev/en/latest/_modules/celery/utils/time.html#get_exponential_backoff_interval)
    """
    # Will be zero if factor equals 0
    countdown = min(maximum, factor * (base**retries))
    # Full jitter according to
    # https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    if full_jitter:
        countdown = random.randrange(countdown + 1)
    # Adjust according to maximum wait time and account for negative values.
    return max(0, countdown)
