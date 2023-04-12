from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from CinManager.forms import FilmForm, ScreenForm, ShowingForm
from CinManager.models import Film, Screen, Showing, Club, ClubRep
from django.contrib.auth.models import User, Group
from django.shortcuts import  render, redirect
from django.contrib import messages
import uuid

#Create your views here.
#Add film function

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

    return userpermission


def add_film_view(request):
    userpermissions = check_permissions(request) #all functions check for cinemamagers status to set nav bar permissions

    if request.method == 'POST':
        form = FilmForm(request.POST)
        if form.is_valid():
            form.save() #submits from if valid - form based on film model
            return redirect('home')
    else:
        form = FilmForm()
    return render(request, 'UWEFlix/filmadd.html', {'form': form, 'userpermissions': userpermissions}) 

def addCinManagers(request):
    userpermissions = check_permissions(request)

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

    return render(request, 'UWEFlix/addcinman.html', {'users': users , 'userpermissions': userpermissions})


def create_club_view(request):
    userpermissions = check_permissions(request)

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
        username = str(uuid.uuid4())[:8]

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
    return render(request, 'UWEFlix/createclub.html', {'userpermissions': userpermissions})

def clubcreatedsucess(request,username,password):
    userpermissions = check_permissions(request)

    #diagnostic print
    print("Username2: " , username)
    print("Password2: " , password)

    return render(request,'UWEFlix/club_created_success.html', {'userpermissions': userpermissions, 'username':username, 'password':password})

#Simple form submit function
def create_screen_view(request):
    userpermissions = check_permissions(request)

    if request.method == 'POST':
        form = ScreenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ScreenForm()
    return render(request, 'UWEFlix/createscreen.html', {'form': form , 'userpermissions': userpermissions})


def create_showing_view(request):
    userpermissions = check_permissions(request)

    films = Film.objects.all()
    screens = Screen.objects.all()

    if request.method == 'POST':
        form = ShowingForm(request.POST)
        if form.is_valid():
            showing = form.save()
            return redirect('home')
    else:
        form = ShowingForm()
    return render(request, 'UWEFlix/createshowing.html', {'form': form, 'films': films, 'screens': screens , 'userpermissions': userpermissions})

#Delete film function
def delete_film(request, film_id):
    userpermissions = check_permissions(request)

    #checks permissions
    if userpermissions == 1:
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


def update_film(request, film_id):
    userpermissions = check_permissions(request)

    #Find instance of selected film
    film = Film.objects.get(pk=film_id)
    form = FilmForm(request.POST or None, instance=film)

    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'UWEFlix/updatefilm.html', {'film':film, 'form':form, 'userpermissions': userpermissions})

def update_club(request, club_id):
    userpermissions = check_permissions(request)

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
    return render(request, 'UWEFlix/editclub.html', {'club': club, 'club_rep': club_rep, 'userpermissions': userpermissions})
