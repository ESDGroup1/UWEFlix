from datetime import datetime
from decimal import Decimal
from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from CinManager.models import ClubRep, Club
from web_project import settings
from .models import Showing, Booking
from Accounts.models import PaymentDetails, Account, Receipt, PersonalReceipt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


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
    price = 0

    if userpermissions == 2:
        club_rep = ClubRep.objects.get(user=request.user)
        club_id = club_rep.club.id
        club = get_object_or_404(Club, id=club_id)
    else:
        club_id = 0

    # Calculate the available seats
    available_seats = showing.screen.capacity - showing.bookedseats

    # Try to get the latest unpurchased booking for the current user and showing
    latest_booking = Booking.objects.filter(showing=showing, user=request.user, purchased=False).last()

    if request.method == 'POST':
        # Get the ticket counts from the form data
        adult_tickets = int(request.POST.get('adult_tickets', 0))
        student_tickets = int(request.POST.get('student_tickets', 0))
        child_tickets = int(request.POST.get('child_tickets', 0))  # set to 0 if not provided

        if userpermissions == 2:
            print("YES 2")
            discount_rate = club.discount_rate / 100
            print("DISCOUNT RATE:", discount_rate)
            priceog = (adult_tickets * 10) + (student_tickets * 8) + (child_tickets * 6)
            print("PRICE OG:", priceog)
            price = priceog - (priceog * discount_rate)
            print("PRICE:",price)
        else:
            # Calculate the total price
            print("NOT 2")
            price = (adult_tickets * 10) + (student_tickets * 8) + (child_tickets * 6)

        if latest_booking:
            # Update the existing Booking object with the new ticket counts and price
            latest_booking.adult_tickets = adult_tickets
            latest_booking.student_tickets = student_tickets
            latest_booking.child_tickets = child_tickets
            latest_booking.price = price
            latest_booking.save()
        else:
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
        # Check if the "Book Showing" button was clicked
        book_showing = request.GET.get('book_showing')

        if book_showing:
            if latest_booking:
                # Render the same page with the latest booking for the current user and showing
                ticketcount = latest_booking.adult_tickets + latest_booking.student_tickets + latest_booking.child_tickets
                context = {'showing': showing, 'latest_booking': latest_booking, 'userpermissions': userpermissions, 'club_id': club_id, 'available_seats': available_seats, 'ticketcount': ticketcount}
                return render(request, 'UWEFlix/add_to_cart.html', context)
            else:
                # Create a new Booking object with default ticket counts
                latest_booking = Booking.objects.create(
                    showing=showing,
                    user=request.user,
                    adult_tickets=0,
                    student_tickets=0,
                    child_tickets=0,
                    purchased=False
                )
                ticketcount = latest_booking.adult_tickets + latest_booking.student_tickets + latest_booking.child_tickets

            # Render the same page with the new Booking object
            context = {'showing': showing, 'latest_booking': latest_booking, 'userpermissions': userpermissions, 'club_id': club_id, 'available_seats': available_seats, 'ticketcount': ticketcount}
            return render(request, 'UWEFlix/add_to_cart.html', context)

        else:
            # Render the same page with the latest booking for the current user and showing, or create a new one if none exists
            if not latest_booking:
                latest_booking = Booking.objects.create(showing=showing, user=request.user)

            ticketcount = latest_booking.adult_tickets + latest_booking.student_tickets + latest_booking.child_tickets
            context = {'showing': showing, 'latest_booking': latest_booking, 'available_seats': available_seats, 'userpermissions': userpermissions, 'club_id': club_id, 'ticketcount': ticketcount}
            return render(request, 'UWEFlix/add_to_cart.html', context)

def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user, purchased=False)

    if request.method == 'POST':
        booking.delete()
        return redirect('film_detail', film_id=booking.showing.film.id)

    return redirect('home')


def payment(request, booking_id):
    userpermissions = check_permissions(request)

    print("BOOKING ID:", booking_id)
    # Get the booking object
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user, purchased=False)

    # Get the user's payment details
    try:
        payment_details = PaymentDetails.objects.get(user=request.user)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        customer = stripe.Customer.create(
            email=request.user.email
        )

        payment_data = {
            'customer': customer['id'],
        }

        # Store the Stripe customer ID in the PaymentDetails object
        payment_details.stripe_customer_id = customer['id']
        payment_details.save()
    except PaymentDetails.DoesNotExist:
        payment_data = {}

    if request.method == 'POST':
        # Calculate the total price
        price = booking.get_price()
        print("FINAL PRICE", price)

        # Create a new Stripe Checkout Session
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'Ticket for ' + booking.showing.film.title,
                        'description': 'Showing at ' + str(booking.showing.date),
                    },
                    'unit_amount': int(price) * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success', args=[booking_id])),
            cancel_url=request.build_absolute_uri(reverse('add_to_cart', args=[booking.showing.id])),
            **payment_data,
        )


        # Store the Session ID in the booking object
        booking.stripe_session_id = session.id
        booking.save()

        # Render the Stripe Checkout page
        context = {'session_id': session.id}
        return render(request, 'UWEFlix/payment.html', context)

    else:
        return redirect('index')
    
def clubrep_payment(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user, purchased=False)
        clubrep = ClubRep.objects.get(user=request.user)
        account = Account.objects.get(club=clubrep.club)
        
        if request.method == 'POST':
            # Deduct the price from the account balance
            account.balance -= booking.price
            account.save()
            
            return redirect('payment_success', booking_id=booking.id)
        
        context = {'booking': booking, 'account': account}
        return render(request, 'UWEFlix/clubrep_payment.html', context)
        
    except Account.DoesNotExist:
        context = {'message': 'Sorry no account for this club was found. Please contact your Account Manager.'}
        return render(request, 'UWEFlix/no_account_found.html', context)


def payment_success(request, booking_id):
    userpermissions = check_permissions(request)
    # Get the booking object
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user, purchased=False)

    # Update the purchased attribute of the booking object
    booking.purchased = True
    booking.save()

    # Update the bookedseats attribute of the showing object
    showing = booking.showing
    showing.bookedseats += booking.get_total_tickets()
    showing.save()

    # Make receipt for Club Rep
    if userpermissions == 2:
        print("Club Rep RECEIPT")
        clubrep = get_object_or_404(ClubRep, user=request.user)
        club = get_object_or_404(Club, clubrep=clubrep)
        account = get_object_or_404(Account, club=club)
        Receipt.objects.create(
            account=account,
            date=datetime.now(),
            showing=booking.showing,
            adult_tickets=booking.adult_tickets,
            student_tickets=booking.student_tickets,
            child_tickets=booking.child_tickets,
            price=booking.get_price()
        )

    # Skip if user is a Guest
    elif userpermissions == 4:
        print("Guest RECEIPT")
        pass

    # Make personal receipt for Customer
    else:
        print("Customer RECEIPT")
        PersonalReceipt.objects.create(
            user=request.user,
            date=datetime.now(),
            showing=booking.showing,
            adult_tickets=booking.adult_tickets,
            student_tickets=booking.student_tickets,
            child_tickets=booking.child_tickets,
            price=booking.get_price()
        )

    context = {'booking': booking, 'userpermissions': userpermissions, 'club_id': club.id}
    return render(request, 'UWEFlix/payment_success.html', context)

