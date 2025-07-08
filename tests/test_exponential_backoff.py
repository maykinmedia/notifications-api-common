from notifications_api_common.exponential_backoff import (
    get_exponential_backoff_interval,
)


def test_backoff_progression_with_various_bases():
    factor = 25
    maximum = 52000
    retries_range = range(0, 7)

    expected_delays = {
        2: [25, 50, 100, 200, 400, 800, 1600],
        3: [25, 75, 225, 675, 2025, 6075, 18225],
        4: [25, 100, 400, 1600, 6400, 25600, 52000],
    }

    for base in [2, 3, 4]:
        for retries, expected_delay in zip(retries_range, expected_delays[base]):
            actual_delay = get_exponential_backoff_interval(
                factor=factor,
                retries=retries,
                maximum=maximum,
                base=base,
                full_jitter=False,
            )
            assert actual_delay == expected_delay, (
                f"Base={base}, Retry={retries}: Expected {expected_delay}, got {actual_delay}"
            )
