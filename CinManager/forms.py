from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError
from CinManager.models import Film, Club, Screen, Showing

class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ['title', 'age_rating', 'duration', 'trailer_description']

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'address', 'contact_number', 'email', 'discount_rate']

class ScreenForm(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ['number', 'capacity']

class ShowingForm(forms.ModelForm):
    class Meta:
        model = Showing
        fields = ['film', 'screen', 'date']