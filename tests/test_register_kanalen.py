from io import StringIO
from unittest.mock import Mock

from django.test.testcases import call_command

import pytest
from furl import furl

from notifications_api_common.kanalen import KANAAL_REGISTRY, Kanaal

from .conftest import NOTIFICATIONS_API_ROOT

KANALEN_LIST_URL = (furl(NOTIFICATIONS_API_ROOT) / "kanaal").url


@pytest.fixture
def override_kanalen():
    kanalen = set(
        (
            Kanaal(
                label="foobar", main_resource=Mock(), kenmerken=("kenmerk1", "kenmerk2")
            ),
            Kanaal(label="boofar", main_resource=Mock(), kenmerken=("kenmerk1",)),
        )
    )

    KANAAL_REGISTRY.clear()
    KANAAL_REGISTRY.update(kanalen)


@pytest.mark.django_db
def test_register_kanalen_success(
    notifications_config, requests_mock, override_kanalen
):
    filter_kanaal_url = furl(KANALEN_LIST_URL).set({"naam": "foobar"}).url
    requests_mock.get(filter_kanaal_url, json=[])
    requests_mock.post(
        KANALEN_LIST_URL,
        json={
            "url": "http://example.com",
            "naam": "string",
            "documentatieLink": "http://example.com",
            "filters": ["string"],
        },
        status_code=201,
    )

    call_command("register_kanalen", kanalen=["foobar"])

    assert len(requests_mock.request_history) == 2

    get_request, post_request = requests_mock.request_history

    assert get_request._request.url == filter_kanaal_url
    assert post_request._request.url == KANALEN_LIST_URL
    assert post_request.json() == {
        "naam": "foobar",
        "documentatieLink": "https://example.com/notifications/kanalen/#foobar",
        "filters": ["kenmerk1", "kenmerk2"],
    }


@pytest.mark.django_db
def test_register_kanalen_from_registry_success(
    notifications_config, requests_mock, override_kanalen
):
    filter_kanaal_url1 = furl(KANALEN_LIST_URL).set({"naam": "foobar"}).url
    filter_kanaal_url2 = furl(KANALEN_LIST_URL).set({"naam": "boofar"}).url

    requests_mock.get(filter_kanaal_url1, json=[])
    requests_mock.post(
        KANALEN_LIST_URL,
        json={
            "url": f"{NOTIFICATIONS_API_ROOT}kanalen/1",
            "naam": "foobar",
            "documentatieLink": "http://example.com",
            "filters": ["string"],
        },
        status_code=201,
    )
    requests_mock.get(filter_kanaal_url2, json=[])
    requests_mock.post(
        KANALEN_LIST_URL,
        json={
            "url": f"{NOTIFICATIONS_API_ROOT}kanalen/2",
            "naam": "boofar",
            "documentatieLink": "http://example.com",
            "filters": ["string"],
        },
        status_code=201,
    )

    call_command("register_kanalen")

    assert len(requests_mock.request_history) == 4

    # kanalen are sorted by label
    first_get_request, first_post_request, second_get_request, second_post_request = (
        requests_mock.request_history
    )

    assert first_get_request.url == filter_kanaal_url2
    assert first_post_request.url == KANALEN_LIST_URL
    assert second_get_request.url == filter_kanaal_url1
    assert second_post_request.url == KANALEN_LIST_URL


@pytest.mark.django_db
def test_register_kanalen_existing_kanalen(
    notifications_config, requests_mock, override_kanalen
):
    """
    Test that already registered kanalen are updated
    """
    filter_kanaal_url1 = furl(KANALEN_LIST_URL).set({"naam": "foobar"}).url
    kanaal_detail_url1 = (furl(KANALEN_LIST_URL) / "1").url

    requests_mock.get(
        filter_kanaal_url1,
        json=[
            {
                "url": kanaal_detail_url1,
                "naam": "foobar",
                "documentatieLink": "http://old.example.com",
                "filters": ["string"],
            }
        ],
    )
    requests_mock.put(
        kanaal_detail_url1,
        json=[
            {
                "url": kanaal_detail_url1,
                "naam": "foobar",
                "documentatieLink": "http://old.example.com",
                "filters": ["string"],
            }
        ],
    )

    filter_kanaal_url2 = furl(KANALEN_LIST_URL).set({"naam": "boofar"}).url
    kanaal_detail_url2 = (furl(KANALEN_LIST_URL) / "2").url

    requests_mock.get(
        filter_kanaal_url2,
        json=[
            {
                "url": kanaal_detail_url2,
                "naam": "foobar",
                "documentatieLink": "http://old.example.com",
                "filters": [],
            }
        ],
    )
    requests_mock.put(
        kanaal_detail_url2,
        json=[
            {
                "url": kanaal_detail_url2,
                "naam": "foobar",
                "documentatieLink": "http://old.example.com",
                "filters": [],
            }
        ],
    )

    call_command("register_kanalen")

    assert len(requests_mock.request_history) == 4

    get_request1, put_request1, get_request2, put_request2 = (
        requests_mock.request_history
    )
    assert get_request1.method == "GET"
    assert get_request1.url == filter_kanaal_url2

    assert put_request1.method == "PUT"
    assert put_request1.url == kanaal_detail_url2
    assert put_request1.json() == {
        "naam": "boofar",
        "documentatieLink": "https://example.com/notifications/kanalen/#boofar",
        "filters": ["kenmerk1"],
    }

    assert get_request2.method == "GET"
    assert get_request2.url == filter_kanaal_url1

    assert put_request2.method == "PUT"
    assert put_request2.url == kanaal_detail_url1
    assert put_request2.json() == {
        "naam": "foobar",
        "documentatieLink": "https://example.com/notifications/kanalen/#foobar",
        "filters": ["kenmerk1", "kenmerk2"],
    }


@pytest.mark.django_db
def test_register_kanalen_unknown_url(
    notifications_config, requests_mock, override_kanalen
):
    filter_kanaal_url = furl(KANALEN_LIST_URL).set({"naam": "foobar"}).url

    requests_mock.get(filter_kanaal_url, status_code=404)

    stderr = StringIO()

    call_command("register_kanalen", kanalen=["foobar"], stderr=stderr)

    partial_failure_message = "Unable to retrieve kanaal foobar"

    assert partial_failure_message in stderr.getvalue()

    assert len(requests_mock.request_history) == 1

    request = requests_mock.request_history[0]

    assert request._request.url == filter_kanaal_url


@pytest.mark.django_db
def test_register_kanalen_incorrect_post(
    notifications_config, requests_mock, override_kanalen
):
    filter_kanaal_url = furl(KANALEN_LIST_URL).set({"naam": "foobar"}).url

    requests_mock.get(filter_kanaal_url, json=[])
    requests_mock.post(KANALEN_LIST_URL, json={"error": "foo"}, status_code=400)

    stderr = StringIO()

    call_command("register_kanalen", kanalen=["foobar"], stderr=stderr)

    partial_failure_message = "Unable to create kanaal foobar"

    assert partial_failure_message in stderr.getvalue()

    assert len(requests_mock.request_history) == 2

    get_request, post_request = requests_mock.request_history

    assert get_request._request.url == filter_kanaal_url
    assert post_request._request.url == KANALEN_LIST_URL


@pytest.mark.django_db
def test_register_kanalen_update_fails(
    notifications_config, requests_mock, override_kanalen
):
    filter_kanaal_url = furl(KANALEN_LIST_URL).set({"naam": "foobar"}).url
    kanaal_detail_url = (furl(KANALEN_LIST_URL) / "1").url
    requests_mock.get(
        filter_kanaal_url,
        json=[
            {
                "url": kanaal_detail_url,
                "naam": "foobar",
                "documentatieLink": "http://old.example.com",
                "filters": ["string"],
            }
        ],
    )
    requests_mock.put(
        kanaal_detail_url,
        json={"error": "foo"},
        status_code=400,
    )

    stderr = StringIO()

    call_command("register_kanalen", kanalen=["foobar"], stderr=stderr)

    partial_failure_message = "Unable to update kanaal foobar"

    assert partial_failure_message in stderr.getvalue()

    assert len(requests_mock.request_history) == 2

    get_request, put_request = requests_mock.request_history

    assert get_request.url == filter_kanaal_url
    assert put_request.url == kanaal_detail_url
