# Generated by Django 4.1.7 on 2023-05-08 16:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CinManager', '0006_showing_bookedseats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='capacity',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(300)]),
        ),
    ]
