from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from CinManager.models import Club, ClubRep, Film, Screen, Showing
from datetime import datetime
from Bookings.models import Booking, deleteRequest
from django.utils import timezone
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserChangeForm

def check_permissions(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Cinema Managers').exists():
            userpermission = 1
        elif request.user.groups.filter(name='Club Representatives').exists():
            userpermission = 2
        elif request.user.groups.filter(name='Account Managers').exists():
            userpermission = 3
        elif request.user.groups.filter(name='Guest').exists():
            userpermission = 4
        else:
            userpermission = 0
    else:
        return redirect('Login')
    return userpermission

def home(request):
    userpermissions = check_permissions(request)
    
    # get the selected date from the form if it exists
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # get all showings for the selected date
            showings = Showing.objects.filter(date__date=selected_date)
            if not showings:
                # show message if there are no showings on the selected date
                messages.warning(request, "Sorry, there are no showings on this date.")
                films = []
            else:
                # get the films that have showings on the selected date
                films = Film.objects.filter(showing__in=showings).distinct()
        except ValueError:
            messages.error(request, "Invalid date format.")
            # show all films if there was an error with the submitted date
            films = Film.objects.all()
    else:
        # show all films by default
        films = Film.objects.all()
        
    for film in films:
        # check if each film has showings
        showings = Showing.objects.filter(film=film)
        if not showings:
            film.has_showings = False
        else:
            film.has_showings = True

    # set the club_id variable if user has permissions 2
    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    else:
        club_id = 0

    print("CLUB ID IS: ",club_id)
    # pass the selected date and club_id as context variables
    context = {
        'films': films,
        'userpermissions': userpermissions,
        'selected_date': selected_date.strftime('%Y-%m-%d') if selected_date else None,
        'club_id': club_id
    }
    return render(request, 'UWEFlix/home.html', context)

def film_detail_view(request, film_id):
    userpermissions = check_permissions(request)
    
    film = get_object_or_404(Film, id=film_id)

    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    else:
        club_id = 0
    
    selected_date = request.GET.get('date')
    print("SELECTED DATE:" , selected_date)
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # get all showings for the selected date and the selected film
            showings = Showing.objects.filter(film=film, date__date=selected_date)
            if not showings:
                # show message if there are no showings for the selected film on the selected date
                messages.warning(request, "Sorry, there are no showings for this film on the selected date.")
        except ValueError:
            showings = Showing.objects.filter(film=film)
    else:
        showings = Showing.objects.filter(film=film)

    # get available seats for each showing
    for showing in showings:
        showing.available_seats = showing.screen.capacity - showing.bookedseats if showing.bookedseats else showing.screen.capacity

    return render(request, 'UWEFlix/filmdetail.html', {'film': film, 'showings': showings, 'userpermissions': userpermissions, 'selected_date': selected_date, 'club_id': club_id})

def view_all_clubs(request):
    userpermissions = check_permissions(request)

    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    else:
        club_id = 0

    #gathers data from db
    clubs = Club.objects.all()
    club_reps = ClubRep.objects.all()
    return render(request, 'UWEFlix/allclubs.html', {'clubs': clubs, 'club_reps': club_reps, 'userpermissions': userpermissions, 'club_id': club_id})

#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("Login")

def error_404(request, exception):
    return render(request, 'UWEFlix/error_404.html', {}, status=404)

def purchased_bookings(request):
    # Get all purchased bookings for the current user
    userpermissions = check_permissions(request)
    purchased_bookings = Booking.objects.filter(user=request.user, purchased=True, showing__date__gt=timezone.now().date())

    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    else:
        club_id = 0

    context = {'bookings': purchased_bookings, 'userpermissions': userpermissions, 'club_id': club_id}
    return render(request, 'UWEFlix/purchased_bookings.html', context)


def profile(request):
    user = request.user
    userpermissions = check_permissions(request)
    if request.method == 'POST':
        # update the user's details
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        # update the user's password, if provided
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
        
        return redirect('profile')

    else:
        form = PasswordChangeForm(user)
    return render(request, 'UWEFlix/profile.html', {'form': form, 'userpermissions': userpermissions})

def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        logout(request)
        return redirect('logout')
    return render(request, 'UWEFlix/delete_account_modal.html')

def confirm_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    userpermissions = check_permissions(request)

    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    
    # Check if deleteRequest already exists for the booking
    existing_request = deleteRequest.objects.filter(booking=booking).exists()
    if existing_request:
        messages.error(request, 'A delete request already exists for this booking.')
        return redirect('purchased_bookings')
    
    delete_request = deleteRequest.objects.create(user=request.user, booking=booking)
    messages.success(request, 'Your request has been sent to the cinema manager.')
    return redirect('purchased_bookings')

def viewclubbookings(request):
    userpermissions = check_permissions(request)
    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    else:
        messages.error(request, "Sorry, No club was found.")
        club_id = 0
        return redirect('home', club_id=club_id)
        
    print("CLUB ID IS: ",club_id)
    bookings = Booking.objects.filter(user=request.user, purchased=True, showing__date__gt=timezone.now().date())
    return render(request, 'UWEFlix/purchased_bookings.html', {'bookings': bookings, 'userpermissions': userpermissions, 'club_id': club_id})