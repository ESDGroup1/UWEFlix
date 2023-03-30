from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render
from CinManager.models import Club, ClubRep, Film, Screen, Showing
from datetime import datetime


# Create your views here.
def is_member_CinemaManager(request):
    if request.user.groups.filter(name='Cinema Managers').exists(): #checks if user is in Cinema Managers django group
        isCinManager = 1 # sets 1 if yes
    else:
        isCinManager = 0
    return isCinManager #returns value to orignal function

from datetime import datetime

def home(request):
    isCinManager = is_member_CinemaManager(request)
    
    # check if a date has been submitted in the form
    date = request.GET.get('date')
    if date:
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            # get all showings for the selected date
            showings = Showing.objects.filter(date=date)
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
            
    return render(request, 'UWEFlix/home.html', {'films': films, 'iscinmanager': isCinManager})


def film_detail_view(request, film_id):
    isCinManager = is_member_CinemaManager(request)

    film = get_object_or_404(Film, id=film_id)
    showings = Showing.objects.filter(film=film)
    if not showings:
        messages.error(request, "This film has no showings.")
    return render(request, 'UWEFlix/filmdetail.html', {'film': film, 'showings': showings, 'iscinmanager': isCinManager})

def view_all_clubs(request):
    isCinManager = is_member_CinemaManager(request)

    #gathers data from db
    clubs = Club.objects.all()
    club_reps = ClubRep.objects.all()
    return render(request, 'UWEFlix/allclubs.html', {'clubs': clubs, 'club_reps': club_reps, 'iscinmanager': isCinManager})

#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("Login")