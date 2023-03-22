from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Authentication.forms import LoginForm, RegistrationForm

# Create your views here.
def login_view(request):
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
			#login(request, user)
			return redirect("Login")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = RegistrationForm()
	return render(request, 'UWEFlix/registration.html', {'form': form})

#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("Login")
