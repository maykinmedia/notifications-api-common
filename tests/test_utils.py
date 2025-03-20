from django.test import override_settings

from notifications_api_common.settings import get_setting


def test_get_settings():
    assert get_setting("SITE_DOMAIN") == "example.com"


@override_settings(SITE_DOMAIN=None)
def test_get_settings_null_value():
    assert get_setting("SITE_DOMAIN") is None
