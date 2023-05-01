from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Film(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    age_rating = models.PositiveSmallIntegerField()
    duration = models.PositiveIntegerField()
    trailer_description = models.TextField()
    imageurl = models.CharField(max_length=1000)

class Screen(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

class Showing(models.Model):
    id = models.AutoField(primary_key=True)
    film = models.ForeignKey(Film, on_delete=models.DO_NOTHING)
    screen = models.ForeignKey(Screen, on_delete=models.DO_NOTHING)
    date = models.DateTimeField()
    bookedseats = models.IntegerField(default=0)

class Club(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    discount_rate = models.PositiveIntegerField(default=0)

class ClubRep(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    dateofbirth = models.DateField(default=datetime.now)
    club = models.OneToOneField(Club, on_delete=models.CASCADE)
#Make a seperate user account for connecting the clubrep - generate a random password for that new user