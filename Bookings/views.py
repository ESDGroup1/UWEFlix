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
    else:
        return redirect('Login')
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

        # Get the latest booking for the current user and showing
        latest_booking = Booking.objects.filter(showing=showing, user=request.user).latest('id')

        # Update the existing Booking object with the new ticket counts and price
        latest_booking.adult_tickets = adult_tickets
        latest_booking.student_tickets = student_tickets
        latest_booking.child_tickets = child_tickets
        latest_booking.price = price
        latest_booking.save()

        # Redirect to the same page to avoid duplicate form submissions
        return redirect('add_to_cart', showing_id=showing_id)

    else:
        # Check if the "Book Showing" button was clicked
        book_showing = request.GET.get('book_showing')

        if book_showing:
            # Get the ticket counts from the latest booking for the current user and showing
            latest_booking = Booking.objects.filter(showing=showing, user=request.user).latest('id')
            adult_tickets = latest_booking.adult_tickets
            student_tickets = latest_booking.student_tickets
            child_tickets = latest_booking.child_tickets

            # Calculate the total price
            price = latest_booking.price

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

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking.delete()
        return redirect('film_detail', film_id=booking.showing.film.id)

    return redirect('home')


