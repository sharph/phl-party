# Generated by Django 4.1.2 on 2022-10-21 04:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("legistar", "0002_legislation_legistar_guid_legislation_legistar_id_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="LegislationSponsors",
            new_name="LegislationSponsor",
        ),
        migrations.CreateModel(
            name="LegislationAction",
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
                ("action", models.CharField(max_length=100)),
                ("action_text", models.TextField(null=True)),
                ("result", models.CharField(max_length=100)),
                ("date", models.DateField()),
                (
                    "legislation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="legistar.legislation",
                    ),
                ),
                (
                    "mover",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mover",
                        to="legistar.person",
                    ),
                ),
                (
                    "seconder",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seconder",
                        to="legistar.person",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActionVote",
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
                ("vote", models.CharField(max_length=20)),
                (
                    "action",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="legistar.legislationaction",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="legistar.person",
                    ),
                ),
            ],
        ),
    ]
