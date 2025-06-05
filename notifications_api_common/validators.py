import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from .settings import get_setting

logger = logging.getLogger(__name__)


@deconstructible
class UntilNowValidator:
    """
    Validate a datetime to not be in the future.

    This means that `now` is included.

    Some leeway can be added with the TIME_LEEWAY setting.
    """

    message = _("Ensure this value is not in the future.")
    code = "future_not_allowed"

    @property
    def limit_value(self):
        return timezone.now() + timedelta(seconds=get_setting("TIME_LEEWAY"))

    def __call__(self, value):
        if value > self.limit_value:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.message == other.message
            and self.code == other.code
        )
