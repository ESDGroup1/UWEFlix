from django.shortcuts import render, get_object_or_404, redirect
from .models import Showing, Booking

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

def add_to_cart(request, showing_id):
    # Get the showing object
    showing = get_object_or_404(Showing, id=showing_id)
    userpermissions = check_permissions(request)

    if request.method == 'POST':
        # Get the ticket counts from the form data
        adult_tickets = int(request.POST.get('adult_tickets', 0))
        student_tickets = int(request.POST.get('student_tickets', 0))
        child_tickets = int(request.POST.get('child_tickets', 0))  # set to 0 if not provided

        # Calculate the total price
        price = (adult_tickets * 10) + (student_tickets * 8) + (child_tickets * 6)

        # Create a new Booking object with the ticket counts and price
        booking = Booking.objects.create(
            showing=showing,
            user=request.user,
            adult_tickets=adult_tickets,
            student_tickets=student_tickets,
            child_tickets=child_tickets,
            price=price,
            purchased=False
        )

        # Redirect to the same page to avoid duplicate form submissions
        return redirect('add_to_cart', showing_id=showing_id)

    else:
        # Get the latest booking for the current user and showing
        latest_booking = Booking.objects.filter(showing=showing, user=request.user).latest('id')
        context = {'showing': showing, 'latest_booking': latest_booking, 'userpermissions': userpermissions}
        return render(request, 'UWEFlix/add_to_cart.html', context)

