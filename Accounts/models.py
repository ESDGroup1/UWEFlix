import datetime
from django.db import models
from django.contrib.auth.models import User
from CinManager.models import *

# Create your models here.
class Account(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    club = models.ForeignKey(Club, on_delete=models.DO_NOTHING)
    cvv = models.CharField(max_length=3)
    expdate = models.DateField(default=datetime.now)
    balance = models.IntegerField(default=0)

class Receipt(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    date = models.DateField(default=datetime.now)
    showing = models.ForeignKey(Showing, on_delete=models.DO_NOTHING)
    adult_tickets = models.PositiveIntegerField(default=0)
    student_tickets = models.PositiveIntegerField(default=0)
    child_tickets = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)

class PersonalReceipt(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateField(default=datetime.now)
    showing = models.ForeignKey(Showing, on_delete=models.DO_NOTHING)
    adult_tickets = models.PositiveIntegerField(default=0)
    student_tickets = models.PositiveIntegerField(default=0)
    child_tickets = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)

class PaymentDetails(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    account_number = models.CharField(max_length=100)
    cvv = models.CharField(max_length=3)
    expdate = models.DateField(default=datetime.now)