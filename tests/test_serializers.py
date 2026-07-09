import pytest

from notifications_api_common.api.serializers import NotificatieSerializer


@pytest.mark.django_db
def test_boolean_fields():
    msg = {
        "kanaal": "personen",
        "source": "test",
        "hoofd_object": "http://testserver",
        "resource": "person",
        "resource_url": "http://testserver",
        "actie": "create",
        "aanmaakdatum": "2022-01-01T00:00:00",
        "kenmerken": {"a": True, "b": False, "c": None},
    }
    serializer = NotificatieSerializer(msg)
    assert serializer.data["kenmerken"] == {"a": True, "b": False, "c": None}
