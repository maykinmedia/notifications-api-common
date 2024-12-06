from notifications_api_common.kanalen import Kanaal
from notifications_api_common.utils import notification_documentation
from testapp.models import Person


def test_generate_docs():
    kanaal = Kanaal(label="dummy", main_resource=Person, kenmerken=("name",))

    result = notification_documentation(kanaal)

    expected = """Deze API publiceert notificaties op het kanaal `dummy`.

**Main resource**

`person`



**Kenmerken**

* `name`: The name of the person

**Resources en acties**
"""

    assert result == expected


def test_kanaal_get_help_text():
    kanaal = Kanaal(label="dummy", main_resource=Person, kenmerken=("name",))
    field = kanaal.get_field(Person, "name")

    assert kanaal.get_help_text(field, "name") == "The name of the person"

    kanaal = Kanaal(
        label="dummy",
        main_resource=Person,
        kenmerken=("name",),
        extra_kwargs={"name": {"help_text": "help text 2"}},
    )
    field = kanaal.get_field(Person, "name")

    assert kanaal.get_help_text(field, "name") == "help text 2"
