# Generated migration for apps/core

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="APICallLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("endpoint", models.CharField(max_length=500)),
                ("status_code", models.PositiveSmallIntegerField()),
                ("latency_ms", models.PositiveIntegerField()),
                ("error_message", models.TextField(blank=True)),
                (
                    "called_at",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
            ],
            options={
                "ordering": ["-called_at"],
            },
        ),
        migrations.AddIndex(
            model_name="apicalllog",
            index=models.Index(
                fields=["called_at", "status_code"],
                name="core_apicalllog_called_status_idx",
            ),
        ),
    ]
