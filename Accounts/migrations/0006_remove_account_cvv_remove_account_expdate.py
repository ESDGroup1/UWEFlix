# Generated by Django 4.1.7 on 2023-05-01 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0005_paymentdetails_stripe_customer_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='cvv',
        ),
        migrations.RemoveField(
            model_name='account',
            name='expdate',
        ),
    ]
