from django.conf import settings
from django.db import models
from CinManager.models import *

# Create your models here.
class Booking(models.Model):
    ADULT = 'Adult'
    STUDENT = 'Student'
    CHILD = 'Child'
    TICKET_TYPES = [
        (ADULT, 'Adult'),
        (STUDENT, 'Student'),
        (CHILD, 'Child'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)
    adult_tickets = models.PositiveIntegerField(default=0)
    student_tickets = models.PositiveIntegerField(default=0)
    child_tickets = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.adult_tickets} adult tickets, {self.student_tickets} student tickets, {self.child_tickets} child tickets for {self.user.username} ({'purchased' if self.purchased else 'not purchased'})"

