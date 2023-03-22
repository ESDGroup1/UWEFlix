from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render
from CinManager.models import Club, ClubRep, Film, Screen, Showing


# Create your views here.
def is_member_CinemaManager(request):
    if request.user.groups.filter(name='Cinema Managers').exists(): #checks if user is in Cinema Managers django group
        isCinManager = 1 # sets 1 if yes
    else:
        isCinManager = 0
    return isCinManager #returns value to orignal function

def home(request):
    isCinManager = is_member_CinemaManager(request)

    print("MANAGER=",isCinManager)
    films = Film.objects.all() #gathring all films
    for film in films:
        showings = Showing.objects.filter(film=film) #checking each film and checking if it has showings 
        if not showings:
            film.has_showings = False
        else:
            film.has_showings = True
    return render(request, 'UWEFlix/home.html', {'films': films, 'iscinmanager': isCinManager}) #send necessary info

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