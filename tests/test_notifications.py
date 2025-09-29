from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from notifications_api_common.models import APITypes, NotificationsConfig, Service


class NotificationsConfigModelTest(TestCase):
    def setUp(self):
        self.config = NotificationsConfig.get_solo()

    @override_settings(SITE_DOMAIN=None)
    def test_clean_fails_without_site_domain(self):
        with self.assertRaises(ValidationError) as cm:
            self.config.full_clean()
        self.assertIn("SITE_DOMAIN environment variable must be set", str(cm.exception))

    @override_settings(SITE_DOMAIN="https://example.com")
    def test_clean_succeeds_with_site_domain(self):
        self.config.full_clean()

    def test_str_without_service(self):
        self.config.notifications_api_service = None
        self.assertIn("no service configured", str(self.config))

    def test_str_with_service(self):
        service = Service.objects.create(
            api_root="https://api.example.com",
            api_type=APITypes.nrc,
            label="Test Service",
        )
        self.config.notifications_api_service = service
        self.config.save()
        self.assertIn("https://api.example.com", str(self.config))

    def test_get_client_without_service_returns_none(self):
        self.config.notifications_api_service = None
        self.config.save()
        client = NotificationsConfig.get_client()
        self.assertIsNone(client)
