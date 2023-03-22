from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    firstname = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def save(self):
        # Get the form data
        username = self.cleaned_data['username']
        firstname = self.cleaned_data['firstname']
        surname = self.cleaned_data['surname']
        email = self.cleaned_data['email']
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        # Validate the form data
        if password1 != password2:
            raise ValidationError("Passwords do not match.")

        # Create a new user account
        user = User.objects.create_user(username=username, first_name=firstname, last_name=surname, email=email, password=password1)
        user.set_password(password1)
        user.save()