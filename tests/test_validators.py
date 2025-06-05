from datetime import datetime

from django.core.exceptions import ValidationError

import pytest
from freezegun import freeze_time

from notifications_api_common.validators import UntilNowValidator


@freeze_time("2021-08-23T14:20:00")
def test_invalid_date():
    validator = UntilNowValidator()
    with pytest.raises(ValidationError) as error:
        validator(datetime(2021, 8, 23, 14, 20, 4))
    assert "Ensure this value is not in the future." in str(error.value)


@freeze_time("2021-08-23T14:20:00")
def test_invalid_date_with_leeway(settings):
    settings.TIME_LEEWAY = 5
    validator = UntilNowValidator()
    validator(datetime(2021, 8, 23, 14, 20, 4))
