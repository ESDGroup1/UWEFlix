# Generated by Django 4.1.7 on 2023-04-24 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0004_alter_paymentdetails_account_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentdetails',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
