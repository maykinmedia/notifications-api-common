# Generated by Django 3.2.15 on 2022-12-06 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications_api_common", "0006_auto_20221018_1406"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationsconfig",
            name="notification_delivery_max_retries",
            field=models.PositiveIntegerField(
                default=5,
                help_text="The maximum number of automatic retries. After this amount of retries, guaranteed delivery stops trying to deliver the message.",
            ),
        ),
        migrations.AlterField(
            model_name="notificationsconfig",
            name="notification_delivery_retry_backoff",
            field=models.PositiveIntegerField(
                default=3,
                help_text="If specified, a factor applied to the exponential backoff. This allows you to tune how quickly automatic retries are performed.",
            ),
        ),
        migrations.AlterField(
            model_name="notificationsconfig",
            name="notification_delivery_retry_backoff_max",
            field=models.PositiveIntegerField(
                default=48,
                help_text="An upper limit in seconds to the exponential backoff time.",
            ),
        ),
    ]
