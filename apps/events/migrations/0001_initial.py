"""
Initial migration for the events app — WeightClass, Fighter, Event, Fight.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WeightClass",
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
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "limit_kg",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Fighter",
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
                ("external_id", models.CharField(max_length=255, unique=True)),
                ("full_name", models.CharField(db_index=True, max_length=200)),
                ("nationality", models.CharField(max_length=100)),
                (
                    "weight_class",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="events.weightclass",
                    ),
                ),
                ("fighting_style", models.CharField(blank=True, max_length=100)),
                ("wins", models.PositiveIntegerField(default=0)),
                ("losses", models.PositiveIntegerField(default=0)),
                ("draws", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Event",
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
                ("external_id", models.CharField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=300)),
                ("date", models.DateTimeField(db_index=True)),
                ("location", models.CharField(max_length=300)),
                ("venue", models.CharField(blank=True, max_length=300)),
                ("broadcast_info", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("upcoming", "Upcoming"),
                            ("live", "Live"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="upcoming",
                        max_length=20,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Fight",
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
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fights",
                        to="events.event",
                    ),
                ),
                (
                    "fighter_a",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fights_as_a",
                        to="events.fighter",
                    ),
                ),
                (
                    "fighter_b",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fights_as_b",
                        to="events.fighter",
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="wins_set",
                        to="events.fighter",
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("ko", "KO/TKO"),
                            ("sub", "Submission"),
                            ("dec", "Decision"),
                            ("dq", "DQ"),
                            ("other", "Other"),
                        ],
                        max_length=10,
                    ),
                ),
                ("is_main_event", models.BooleanField(default=False)),
                ("bout_order", models.PositiveSmallIntegerField(default=0)),
            ],
        ),
    ]
