import pytest
from django_setup_configuration.exceptions import ConfigurationRunFailed
from django_setup_configuration.test_utils import execute_single_step
from zgw_consumers.test.factories import ServiceFactory

from notifications_api_common.contrib.setup_configuration.steps import (
    NotificationSubscriptionConfigurationStep,
)
from notifications_api_common.models import NotificationsConfig, Subscription

CONFIG_FILE_PATH = "tests/files/setup_config_subscriptions_config.yaml"


@pytest.mark.django_db
def test_execute_configuration_step_success():
    config = NotificationsConfig.get_solo()
    config.notifications_api_service = ServiceFactory.create(
        slug="notifs-api", api_root="http://notificaties.local/api/v1/"
    )
    config.save()

    execute_single_step(
        NotificationSubscriptionConfigurationStep, yaml_source=CONFIG_FILE_PATH
    )

    value = list(
        Subscription.objects.values_list(
            "identifier",
            "client_id",
            "secret",
            "channels",
            "callback_url",
            "_subscription",
        )
    )
    expected = [
        (
            "my-subscription",
            "the-client",
            "supersecret",
            ["Foo", "Bar"],
            "http://my/callback",
            "http://notificaties.local/api/v1/abonnement/0f616bfd-aacc-4d85-a140-2af17a56217b",
        ),
        (
            "my-other-subscription",
            "the-client",
            "supersecret",
            ["Fuh", "Bahr"],
            "http://my/other-callback",
            "http://notificaties.local/api/v1/abonnement/a33cf110-06b6-454e-b7e9-5139c172ca9a",
        ),
    ]

    assert value == expected


@pytest.mark.django_db
def test_existing_items_are_updated():
    config = NotificationsConfig.get_solo()
    config.notifications_api_service = ServiceFactory.create(
        slug="notifs-api", api_root="http://notificaties.local/api/v1/"
    )
    config.save()

    Subscription.objects.create(
        identifier="my-subscription",
        callback_url="http://my/initial-callback",
        client_id="the-old-client",
        secret="secretsuper",
        channels=["Fuzz"],
    )

    execute_single_step(
        NotificationSubscriptionConfigurationStep, yaml_source=CONFIG_FILE_PATH
    )

    value = list(
        Subscription.objects.values_list(
            "identifier",
            "client_id",
            "secret",
            "channels",
            "callback_url",
            "_subscription",
        )
    )
    expected = [
        # Updated
        (
            "my-subscription",
            "the-client",
            "supersecret",
            ["Foo", "Bar"],
            "http://my/callback",
            "http://notificaties.local/api/v1/abonnement/0f616bfd-aacc-4d85-a140-2af17a56217b",
        ),
        # Created
        (
            "my-other-subscription",
            "the-client",
            "supersecret",
            ["Fuh", "Bahr"],
            "http://my/other-callback",
            "http://notificaties.local/api/v1/abonnement/a33cf110-06b6-454e-b7e9-5139c172ca9a",
        ),
    ]

    assert value == expected


@pytest.mark.django_db
def test_missing_notifications_service_raises():
    config = NotificationsConfig.get_solo()
    config.notifications_api_service = None
    config.save()

    with pytest.raises(ConfigurationRunFailed) as excinfo:
        execute_single_step(
            NotificationSubscriptionConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

    assert (
        str(excinfo.value)
        == "No Notifications API Service configured. Please ensure you've first run NotificationConfigurationStep"
    )


@pytest.mark.django_db
def test_no_items_raises():
    config = NotificationsConfig.get_solo()
    config.notifications_api_service = ServiceFactory.create(
        slug="notifs-api", api_root="http://notificaties.local/api/v1/"
    )
    config.save()

    with pytest.raises(ConfigurationRunFailed) as excinfo:
        execute_single_step(
            NotificationSubscriptionConfigurationStep,
            object_source={"notifications_subscriptions_config": {"items": []}},
        )

    assert str(excinfo.value) == "You must configure at least one subscription"
