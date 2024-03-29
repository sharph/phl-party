# Generated by Django 5.0 on 2024-02-14 18:08

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legistar', '0007_person_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='name', unique=True),
        ),
    ]
