from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render
from CinManager.models import Club, ClubRep, Film, Screen, Showing
from datetime import datetime
from Bookings.models import Booking
from django.utils import timezone

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
            messages.error(request, "Invalid date format.")
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
    purchased_bookings = Booking.objects.filter(user=request.user, purchased=True, showing__date__gt=timezone.now().date())

    context = {'bookings': purchased_bookings}
    return render(request, 'UWEFlix/purchased_bookings.html', context)
