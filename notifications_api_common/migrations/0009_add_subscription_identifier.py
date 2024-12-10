from django.db import migrations, models


def generate_missing_identifiers(apps, schema_editor):
    Subscription = apps.get_model("notifications_api_common", "Subscription")

    count = 1
    for subscription in Subscription.objects.all():
        while Subscription.objects.filter(
            identifier=f"subscription-{count:02d}"
        ).exists():
            count += 1

        subscription.identifier = f"subscription-{count:02d}"
        subscription.save(update_fields=["identifier"])
        count += 1


class Migration(migrations.Migration):

    dependencies = [
        (
            "notifications_api_common",
            "0008_merge_0006_auto_20221213_0214_0007_auto_20221206_0414",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="identifier",
            field=models.SlugField(
                help_text="A human-friendly identifier to refer to this subscription.",
                max_length=64,
                null=True,
                blank=True,
                unique=True,
            ),
        ),
        migrations.RunPython(
            generate_missing_identifiers,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="subscription",
            name="identifier",
            field=models.SlugField(
                help_text="A human-friendly identifier to refer to this subscription.",
                max_length=64,
                unique=True,
                blank=False,
                null=False,
            ),
        ),
    ]
