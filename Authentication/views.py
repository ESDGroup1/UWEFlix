from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from Authentication.forms import LoginForm, RegistrationForm

# Create your views here.
def login_view(request):
    # Create user groups if they don't exist
    Group.objects.get_or_create(name='Guest')
    Group.objects.get_or_create(name='Cinema Managers')
    Group.objects.get_or_create(name='Club Representatives')
    Group.objects.get_or_create(name='Account Managers')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Login the user
                login(request, user)
                return redirect("home")
            else:
                # Authentication failed
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'UWEFlix/login.html', {'form': form})

def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("Login")
    else:
        form = RegistrationForm()
    return render(request, 'UWEFlix/registration.html', {'form': form})

def login_guest_view(request):
    # Check if the guest user exists
    try:
        guest_user = User.objects.get(username='guest')
    except User.DoesNotExist:
        # Create the guest user
        guest_user = User.objects.create_user(username='guest', password='d63ztyyyX5XptU!')

    # Authenticate the guest user
    user = authenticate(request, username='guest', password='d63ztyyyX5XptU!')

    if user is not None:
        # Login the user
        login(request, user)

        # Add guest user to 'Guest' group if not already a member
        guest_group = Group.objects.get(name='Guest')
        if not guest_group.user_set.filter(pk=user.pk).exists():
            guest_group.user_set.add(user)

        return redirect("home")
    else:
        # Authentication failed
        messages.error(request, "Guest login failed.")

    return redirect("Login")

#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("Login")
