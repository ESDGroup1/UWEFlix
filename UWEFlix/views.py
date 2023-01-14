from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from UWEFlix.forms import LoginForm, FilmForm, ClubForm, RegistrationForm, ScreenForm, ShowingForm
from UWEFlix.models import Film, Screen, Showing, Club, ClubRep
from django.contrib.auth.models import User, Group
from django.shortcuts import  render, redirect
from django.contrib import messages

# Create your views here.

#Permission gathering function
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

#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("Login")


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

#Add film function
def add_film_view(request):
    isCinManager = is_member_CinemaManager(request) #all functions check for cinemamagers status to set nav bar permissions

    if request.method == 'POST':
        form = FilmForm(request.POST)
        if form.is_valid():
            form.save() #submits from if valid - form based on film model
            return redirect('home')
    else:
        form = FilmForm()
    return render(request, 'UWEFlix/filmadd.html', {'form': form, 'iscinmanager': isCinManager}) 

def addCinManagers(request):
    isCinManager = is_member_CinemaManager(request)

    # Only allow users who are already in the Cinema Managers group to access this page
    if not request.user.groups.filter(name='Cinema Managers').exists():
        return redirect('home')

    # Get all users who are not already in the Cinema Managers group
    users = User.objects.exclude(groups__name='Cinema Managers')

    if request.method == 'POST':
        # Get the user that the logged in user wants to add to the group
        user_id = request.POST['user']
        user = User.objects.get(id=user_id)

        # Add the user to the Cinema Managers group
        group = Group.objects.get(name='Cinema Managers')
        group.user_set.add(user)

        return redirect('home')

    return render(request, 'UWEFlix/addcinman.html', {'users': users , 'iscinmanager': isCinManager})


def create_club_view(request):
    isCinManager = is_member_CinemaManager(request)

    if request.method == 'POST':

        # Get the club data from the form
        name = request.POST['name']
        address = request.POST['address']
        contact_number = request.POST['contact_number']
        email = request.POST['email']
        discount_rate = request.POST['discount_rate']
        account_number = request.POST['account_number']
        cvv = request.POST['cvv']
        expdate = request.POST['expdate']
        
        # Create new Club instance
        club = Club(name=name, address=address, contact_number=contact_number, email=email, discount_rate=discount_rate, account_number=account_number, cvv=cvv, expdate=expdate)
        club.save()
        
        # Create new user for club rep
        first_name = request.POST['firstname']
        last_name = request.POST['surname']
        password = User.objects.make_random_password()

        dateofbirth = request.POST['dateofbirth']
        
        rawname = last_name + name
        username = rawname.replace(" ", "")

        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email) #create new user instance with gathered and generated info
        user.save()
    
        
        # Create new ClubRep instance and tie it to the new user and club
        clubrep = ClubRep(user=user, club=club, dateofbirth=dateofbirth)
        clubrep.save()

        #diagnostic print
        print("Username: " , username)
        print("Password: " , password)
        
        #send to page which will show the generated credentials to user
        return redirect('clubcreatedsucess', username=username, password=password)
    return render(request, 'UWEFlix/createclub.html', {'iscinmanager': isCinManager})

def clubcreatedsucess(request,username,password):
    isCinManager = is_member_CinemaManager(request)

    #diagnostic print
    print("Username2: " , username)
    print("Password2: " , password)

    return render(request,'UWEFlix/club_created_success.html', {'iscinmanager': isCinManager, 'username':username, 'password':password})

#Simple form submit function
def create_screen_view(request):
    isCinManager = is_member_CinemaManager(request)

    if request.method == 'POST':
        form = ScreenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ScreenForm()
    return render(request, 'UWEFlix/createscreen.html', {'form': form , 'iscinmanager': isCinManager})


def create_showing_view(request):
    isCinManager = is_member_CinemaManager(request)

    films = Film.objects.all()
    screens = Screen.objects.all()

    if request.method == 'POST':
        form = ShowingForm(request.POST)
        if form.is_valid():
            showing = form.save()
            return redirect('home')
    else:
        form = ShowingForm()
    return render(request, 'UWEFlix/createshowing.html', {'form': form, 'films': films, 'screens': screens , 'iscinmanager': isCinManager})


def film_detail_view(request, film_id):
    isCinManager = is_member_CinemaManager(request)

    film = get_object_or_404(Film, id=film_id)
    showings = Showing.objects.filter(film=film)
    if not showings:
        messages.error(request, "This film has no showings.")
    return render(request, 'UWEFlix/filmdetail.html', {'film': film, 'showings': showings, 'iscinmanager': isCinManager})


#Delete film function
def delete_film(request, film_id):
    isCinManager = is_member_CinemaManager(request)

    #checks permissions
    if isCinManager == 1:
        film = get_object_or_404(Film, id=film_id) #gathers selected film
        showings = Showing.objects.filter(film=film)
        if showings: #checks if films has showing, films with showings will not be deleted, this is in place as a safety measure as delete button is not visible when showings are present
            messages.error(request, "This film has showings, you can't delete it.")
        else:
            film.delete()
            messages.success(request, "Film deleted.")
        return redirect('home')
    else:
        print("ACCESS DENIED")

#Shows list of clubs
def view_all_clubs(request):
    isCinManager = is_member_CinemaManager(request)

    #gathers data from db
    clubs = Club.objects.all()
    club_reps = ClubRep.objects.all()
    return render(request, 'UWEFlix/allclubs.html', {'clubs': clubs, 'club_reps': club_reps, 'iscinmanager': isCinManager})


def update_film(request, film_id):
    isCinManager = is_member_CinemaManager(request)

    #Find instance of selected film
    film = Film.objects.get(pk=film_id)
    form = FilmForm(request.POST or None, instance=film)

    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'UWEFlix/updatefilm.html', {'film':film, 'form':form, 'iscinmanager': isCinManager})

def update_club(request, club_id):
    isCinManager = is_member_CinemaManager(request)

    #Find instance of selected club and connect it to club rep
    club = Club.objects.get(pk=club_id)
    club_rep = ClubRep.objects.get(club=club)

    if request.method == 'POST':
        
        #Gather data
        club.name = request.POST['name']
        club.address = request.POST['address']
        club.contact_number = request.POST['contact_number']
        club.email = request.POST['email']
        club.discount_rate = request.POST['discount_rate']
        club.account_number = request.POST['account_number']
        club.cvv = request.POST['cvv']
        club.expdate = request.POST['expdate']
        club.save()

        club_rep.user.first_name = request.POST['first_name']
        club_rep.user.last_name = request.POST['last_name']
        club_rep.user.email = request.POST['email']
        club_rep.dateofbirth = request.POST['dateofbirth']
        club_rep.user.save()
        club_rep.save()

        return redirect('home')
    return render(request, 'UWEFlix/editclub.html', {'club': club, 'club_rep': club_rep, 'iscinmanager': isCinManager})







