from django.db import models
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    name = models.CharField(
        _("name"), help_text=_("The name of the person"), max_length=50
    )
    address_street = models.CharField(_("street name"), max_length=255)
    address_number = models.CharField(_("house number"), max_length=10)
