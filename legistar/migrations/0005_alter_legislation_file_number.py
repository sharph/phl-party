# Generated by Django 4.1.2 on 2022-10-21 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("legistar", "0004_legislation_sponsors_delete_legislationsponsor"),
    ]

    operations = [
        migrations.AlterField(
            model_name="legislation",
            name="file_number",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
