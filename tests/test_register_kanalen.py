from io import StringIO
from unittest.mock import Mock, patch
from urllib.parse import urlencode

from django.test.testcases import call_command

import pytest

from notifications_api_common.kanalen import KANAAL_REGISTRY, Kanaal

kanalen = set(
    (
        Kanaal(label="foobar", main_resource=Mock()),
        Kanaal(label="boofar", main_resource=Mock()),
    )
)

KANAAL_REGISTRY.clear()
KANAAL_REGISTRY.update(kanalen)


@pytest.mark.django_db
def test_register_kanalen_success(notifications_config, requests_mock):
    kanaal_url = f"{notifications_config.notifications_api_service.api_root}kanaal"
    params = urlencode(dict(naam="foobar"))

    requests_mock.get(f"{kanaal_url}?{params}", json=[])

    requests_mock.post(
        kanaal_url,
        json={
            "url": "http://example.com",
            "naam": "string",
            "documentatieLink": "http://example.com",
            "filters": ["string"],
        },
        status_code=201,
    )

    reverse_patch = (
        "notifications_api_common.management.commands.register_kanalen.reverse"
    )

    with patch(reverse_patch) as mocked_reverse:
        mocked_reverse.return_value = "/notifications/kanalen"

        call_command("register_kanalen", kanalen=["foobar"])

    assert len(requests_mock.request_history) == 2

    get_request = requests_mock.request_history[0]

    assert get_request._request.url == f"{kanaal_url}?{params}"

    post_request = requests_mock.request_history[1]

    assert post_request._request.url == kanaal_url


@pytest.mark.django_db
def test_register_kanalen_from_registry_success(notifications_config, requests_mock):
    kanaal_url = f"{notifications_config.notifications_api_service.api_root}kanaal"

    url_mapping = {
        kanaal.label: f"{kanaal_url}?{urlencode(dict(naam=kanaal.label))}"
        for kanaal in kanalen
    }

    for kanaal in kanalen:
        requests_mock.get(url_mapping[kanaal.label], json=[])

        requests_mock.post(
            kanaal_url,
            json={
                "url": "http://example.com",
                "naam": kanaal.label,
                "documentatieLink": "http://example.com",
                "filters": ["string"],
            },
            status_code=201,
        )

    reverse_patch = (
        "notifications_api_common.management.commands.register_kanalen.reverse"
    )

    with patch(reverse_patch) as mocked_reverse:
        mocked_reverse.return_value = "/notifications/kanalen"

        call_command("register_kanalen")

    assert len(requests_mock.request_history) == 4

    # kanalen are sorted by label
    first_get_request = requests_mock.request_history[0]
    assert first_get_request._request.url == url_mapping["boofar"]

    first_post_request = requests_mock.request_history[1]
    assert first_post_request._request.url == kanaal_url

    second_get_request = requests_mock.request_history[2]
    assert second_get_request._request.url == url_mapping["foobar"]

    second_post_request = requests_mock.request_history[3]
    assert second_post_request._request.url == kanaal_url


@pytest.mark.django_db
def test_register_kanalen_existing_kanalen(notifications_config, requests_mock):
    """
    Test that already registered kanalen does not cause issues
    """
    kanaal_url = f"{notifications_config.notifications_api_service.api_root}kanaal"
    params = urlencode(dict(naam="foobar"))

    requests_mock.get(
        f"{kanaal_url}?{params}",
        json=[
            {
                "url": "http://example.com",
                "naam": "foobar",
                "documentatieLink": "http://example.com",
                "filters": ["string"],
            }
        ],
    )

    call_command("register_kanalen", kanalen=["foobar"])

    assert len(requests_mock.request_history) == 1

    request = requests_mock.request_history[0]

    assert request._request.url == f"{kanaal_url}?{params}"


@pytest.mark.django_db
def test_register_kanalen_unknown_url(notifications_config, requests_mock):
    kanaal_url = f"{notifications_config.notifications_api_service.api_root}kanaal"
    params = urlencode(dict(naam="foobar"))

    requests_mock.get(f"{kanaal_url}?{params}", status_code=404)

    stderr = StringIO()

    call_command("register_kanalen", kanalen=["foobar"], stderr=stderr)

    partial_failure_message = "Unable to retrieve kanaal foobar"

    assert partial_failure_message in stderr.getvalue()

    assert len(requests_mock.request_history) == 1

    request = requests_mock.request_history[0]

    assert request._request.url == f"{kanaal_url}?{params}"


@pytest.mark.django_db
def test_register_kanalen_incorrect_post(notifications_config, requests_mock):
    kanaal_url = f"{notifications_config.notifications_api_service.api_root}kanaal"
    params = urlencode(dict(naam="foobar"))

    requests_mock.get(f"{kanaal_url}?{params}", json=[])

    requests_mock.post(kanaal_url, json={"error": "foo"}, status_code=400)

    stderr = StringIO()

    reverse_patch = (
        "notifications_api_common.management.commands.register_kanalen.reverse"
    )

    with patch(reverse_patch) as mocked_reverse:
        mocked_reverse.return_value = "/notifications/kanalen"

        call_command("register_kanalen", kanalen=["foobar"], stderr=stderr)

    partial_failure_message = "Unable to create kanaal foobar"

    assert partial_failure_message in stderr.getvalue()

    assert len(requests_mock.request_history) == 2

    get_request = requests_mock.request_history[0]

    assert get_request._request.url == f"{kanaal_url}?{params}"

    post_request = requests_mock.request_history[1]

    assert post_request._request.url == kanaal_url
