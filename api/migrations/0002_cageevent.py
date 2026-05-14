# Generated manually for CageEvent journal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CageEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("pigeon_assigned", "Pigeon affecté"),
                            ("pigeon_removed", "Pigeon retiré de la cage"),
                            ("couple_assigned", "Couple affecté"),
                            ("couple_removed", "Couple retiré de la cage"),
                            ("cage_cleaned", "Cage nettoyée"),
                            ("health_check", "Contrôle sanitaire"),
                        ],
                        max_length=32,
                    ),
                ),
                ("meta", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "cage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="api.cage",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
