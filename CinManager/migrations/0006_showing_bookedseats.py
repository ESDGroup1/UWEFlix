# Generated by Django 4.1.7 on 2023-05-01 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CinManager', '0005_alter_club_discount_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='showing',
            name='bookedseats',
            field=models.IntegerField(default=0),
        ),
    ]
