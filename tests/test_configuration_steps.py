import pytest
from django_setup_configuration.test_utils import execute_single_step
from zgw_consumers.test.factories import ServiceFactory

from notifications_api_common.contrib.setup_configuration.steps import (
    NotificationConfigurationStep,
)
from notifications_api_common.models import NotificationsConfig

CONFIG_FILE_PATH = "tests/files/setup_config_notifications_config.yaml"
CONFIG_FILE_PATH_NO_SERVICE = (
    "tests/files/setup_config_notifications_config_no_service.yaml"
)


@pytest.mark.django_db
def test_execute_configuration_step_success():
    service = ServiceFactory.create(
        slug="notifs-api", api_root="http://notificaties.local/api/v1/"
    )

    execute_single_step(NotificationConfigurationStep, yaml_source=CONFIG_FILE_PATH)

    config = NotificationsConfig.get_solo()

    assert config.notifications_api_service == service
    assert config.notification_delivery_max_retries == 1
    assert config.notification_delivery_retry_backoff == 2
    assert config.notification_delivery_retry_backoff_max == 3


@pytest.mark.django_db
def test_execute_configuration_step_update_existing():
    service1 = ServiceFactory.create(
        slug="other-api", api_root="http://other-notificaties.local/api/v1/"
    )
    service2 = ServiceFactory.create(
        slug="notifs-api", api_root="http://notificaties.local/api/v1/"
    )

    config = NotificationsConfig.get_solo()
    config.notifications_api_service = service1
    config.notification_delivery_max_retries = 1
    config.notification_delivery_retry_backoff = 2
    config.notification_delivery_retry_backoff_max = 3
    config.save()

    execute_single_step(NotificationConfigurationStep, yaml_source=CONFIG_FILE_PATH)

    config = NotificationsConfig.get_solo()

    assert config.notifications_api_service == service2
    assert config.notification_delivery_max_retries == 1
    assert config.notification_delivery_retry_backoff == 2
    assert config.notification_delivery_retry_backoff_max == 3


@pytest.mark.django_db
def test_execute_configuration_step_without_service_success():
    execute_single_step(
        NotificationConfigurationStep, yaml_source=CONFIG_FILE_PATH_NO_SERVICE
    )

    config = NotificationsConfig.get_solo()

    assert config.notifications_api_service is None
    assert config.notification_delivery_max_retries == 1
    assert config.notification_delivery_retry_backoff == 2
    assert config.notification_delivery_retry_backoff_max == 3


@pytest.mark.django_db
def test_execute_configuration_step_idempotent():
    service = ServiceFactory.create(
        slug="notifs-api", api_root="http://notificaties.local/api/v1/"
    )

    def make_assertions():
        config = NotificationsConfig.get_solo()

        assert config.notifications_api_service == service
        assert config.notification_delivery_max_retries == 1
        assert config.notification_delivery_retry_backoff == 2
        assert config.notification_delivery_retry_backoff_max == 3

    execute_single_step(NotificationConfigurationStep, yaml_source=CONFIG_FILE_PATH)

    make_assertions()

    execute_single_step(NotificationConfigurationStep, yaml_source=CONFIG_FILE_PATH)

    make_assertions()
