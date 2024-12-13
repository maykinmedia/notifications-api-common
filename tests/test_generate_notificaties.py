from unittest.mock import mock_open, patch

from django.test.testcases import call_command

import pytest

EXPECTED_OUTPUT = """## Notificaties
## Berichtkenmerken voor Notifications API Common API

Kanalen worden typisch per component gedefinieerd. Producers versturen berichten op bepaalde kanalen,
consumers ontvangen deze. Consumers abonneren zich via een notificatiecomponent (zoals <a href="https://notificaties-api.vng.cloud/api/v1/schema/" rel="nofollow">https://notificaties-api.vng.cloud/api/v1/schema/</a>) op berichten.

Hieronder staan de kanalen beschreven die door deze component gebruikt worden, met de kenmerken bij elk bericht.

De architectuur van de notificaties staat beschreven op <a href="https://github.com/VNG-Realisatie/notificaties-api" rel="nofollow">https://github.com/VNG-Realisatie/notificaties-api</a>.


### personen

**Kanaal**
`personen`

**Main resource**

`person`



**Kenmerken**

* `name`: The name of the person
* `address_street`: custom help text

**Resources en acties**


* <code>person</code>: create, update, destroy


"""


@pytest.mark.django_db
@patch(
    "notifications_api_common.management.commands.generate_notificaties.open",
    new_callable=mock_open,
)
def test_generate_notificaties(mock_file):
    call_command("generate_notificaties", output_file=["foobar"])

    mock_file().write.assert_called_once_with(EXPECTED_OUTPUT)
