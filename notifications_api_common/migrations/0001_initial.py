# Generated by Django 3.2.14 on 2022-07-04 13:34

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NotificationsConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "api_root",
                    models.URLField(
                        default="https://notificaties-api.vng.cloud/api/v1/",
                        unique=True,
                        verbose_name="api root",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificatiescomponentconfiguratie",
            },
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "callback_url",
                    models.URLField(
                        help_text="Where to send the notifications (webhook url)",
                        verbose_name="callback url",
                    ),
                ),
                (
                    "client_id",
                    models.CharField(
                        help_text="Client ID to construct the auth token",
                        max_length=50,
                        verbose_name="client ID",
                    ),
                ),
                (
                    "secret",
                    models.CharField(
                        help_text="Secret to construct the auth token",
                        max_length=50,
                        verbose_name="client secret",
                    ),
                ),
                (
                    "channels",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100),
                        help_text="Comma-separated list of channels to subscribe to",
                        size=None,
                        verbose_name="channels",
                    ),
                ),
                (
                    "_subscription",
                    models.URLField(
                        blank=True,
                        editable=False,
                        help_text="Subscription as it is known in the NC",
                        verbose_name="NC subscription",
                    ),
                ),
                (
                    "config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="notifications_api_common.notificationsconfig",
                    ),
                ),
            ],
            options={
                "verbose_name": "Webhook subscription",
                "verbose_name_plural": "Webhook subscriptions",
            },
        ),
    ]
