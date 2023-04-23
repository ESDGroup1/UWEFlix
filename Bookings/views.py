from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from CinManager.models import ClubRep
from web_project import settings
from .models import Showing, Booking
import stripe


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

    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
    else:
        club_id = 0

    if request.method == 'POST':
        # Get the ticket counts from the form data
        adult_tickets = int(request.POST.get('adult_tickets', 0))
        student_tickets = int(request.POST.get('student_tickets', 0))
        child_tickets = int(request.POST.get('child_tickets', 0))  # set to 0 if not provided

        # Calculate the total price
        price = (adult_tickets * 10) + (student_tickets * 8) + (child_tickets * 6)

        # Try to get the latest booking for the current user and showing
        try:
            latest_booking = Booking.objects.filter(showing=showing, user=request.user).latest('id')
        except Booking.DoesNotExist:
            # If no booking exists, create a new one
            latest_booking = Booking.objects.create(showing=showing, user=request.user)

        # Update the existing or new Booking object with the new ticket counts and price
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
            try:
                latest_booking = Booking.objects.filter(showing=showing, user=request.user).latest('id')
            except Booking.DoesNotExist:
                # If no booking exists, create a new one with default ticket counts
                latest_booking = Booking.objects.create(
                    showing=showing,
                    user=request.user,
                    adult_tickets=0,
                    student_tickets=0,
                    child_tickets=0,
                    purchased=False
                )

            # Calculate the total price
            price = latest_booking.get_price()

            # Create a new Booking object with the ticket counts and price
            booking = Booking.objects.create(
                showing=showing,
                user=request.user,
                adult_tickets=latest_booking.adult_tickets,
                student_tickets=latest_booking.student_tickets,
                child_tickets=latest_booking.child_tickets,
                price=price,
                purchased=False
            )

            # Redirect to the same page to avoid duplicate form submissions
            return redirect('add_to_cart', showing_id=showing_id)

        else:
            # Get the latest booking for the current user and showing, or create a new one if none exists
            try:
                latest_booking = Booking.objects.filter(showing=showing, user=request.user).latest('id')
            except Booking.DoesNotExist:
                latest_booking = Booking.objects.create(showing=showing, user=request.user)

            context = {'showing': showing, 'latest_booking': latest_booking, 'userpermissions': userpermissions,'club_id': club_id}
            return render(request, 'UWEFlix/add_to_cart.html', context)


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking.delete()
        return redirect('film_detail', film_id=booking.showing.film.id)

    return redirect('home')


def payment(request, booking_id):
    if request.method == 'POST':
        # Get the user's cart data
        try:
            latest_booking = Booking.objects.filter(
                user=request.user, purchased=False).latest('id')
        except Booking.DoesNotExist:
            return redirect('index')

        # Calculate the total price
        price = latest_booking.get_price()

        # Create a new Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'name': 'Ticket for ' + latest_booking.showing.film.title,
                'description': 'Showing at ' + str(latest_booking.showing.datetime),
                'amount': price * 100,
                'currency': 'usd',
                'quantity': latest_booking.get_total_tickets(),
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )

        # Store the Session ID in the latest booking object
        latest_booking.stripe_session_id = session.id
        latest_booking.save()

        # Render the Stripe Checkout page
        context = {'session_id': session.id}
        return render(request, 'UWEFlix/payment.html', context)

    else:
        return redirect('index')
