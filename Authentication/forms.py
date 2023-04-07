from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError
import re
from django.core.exceptions import ValidationError

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

    def validate_password(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must include an uppercase letter.")

        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must include a number.")

        if not re.search(r'[~!@#$%^&*()_+=-`/\|?.,<>\[\]{};:\'\"\\]', password):
            raise ValidationError("Password must include a special character.")

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        self.validate_password(password1)
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data['password2']
        self.validate_password(password2)
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.", code='password_mismatch')

        return cleaned_data

    def save(self):
        # Get the form data
        username = self.cleaned_data['username']
        firstname = self.cleaned_data['firstname']
        surname = self.cleaned_data['surname']
        email = self.cleaned_data['email']
        password1 = self.cleaned_data['password1']

        # Create a new user account
        user = User.objects.create_user(username=username, first_name=firstname, last_name=surname, email=email, password=password1)
        user.set_password(password1)
        user.save()

        return user
