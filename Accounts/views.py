from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from Accounts.forms import PaymentDetailsForm
from Accounts.models import PaymentDetails
from django.shortcuts import render
from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import Account, ClubRep, Club

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


def edit_payment_details(request):
    userpermissions = check_permissions(request)
    # get the PaymentDetails object associated with the logged in user
    payment_details, created = PaymentDetails.objects.get_or_create(
        user=request.user)

    if request.method == 'POST':
        # update the payment details object with the new form data
        payment_details_form = PaymentDetailsForm(
            request.POST, instance=payment_details)
        if payment_details_form.is_valid():
            payment_details_form.save()
            print("PAYMENT DETAILS SUCCESS")
            messages.success(request, 'Payment details updated successfully')
            return redirect('home')
        else:
            print(payment_details_form.errors)
            print("PAYMENT DETAILS FAIL")
            messages.error(request, 'Error updating payment details')
    else:
        print("PAYMENT DETAILS ELSE")
        payment_details_form = PaymentDetailsForm(instance=payment_details)

    context = {'payment_details_form': payment_details_form,
               'userpermissions': userpermissions}
    return render(request, 'UWEFlix/edit_payment_details.html', context)


def club_list(request):
    userpermissions = check_permissions(request)

    clubs = Club.objects.all()
    club_data = []
    for club in clubs:
        account_exists = Account.objects.filter(club=club).exists()
        if account_exists:
            print("EXISTS ACCOUNT")
            button_text = 'View Account'
        else:
            print("NOT EXISTS ACCOUNT")
            button_text = 'Create Account'
        club_data.append({'club': club, 'button_text': button_text})
    context = {'club_data': club_data, 'userpermissions': userpermissions}
    return render(request, 'UWEFlix/club_list.html', context)


def create_or_view_account(request, club_id):
    print("TRIGGERED CREATE_OR_VIEW")
    club = get_object_or_404(Club, id=club_id)
    account_exists = Account.objects.filter(club=club).exists()
    if account_exists:
        # View account page
        print("TRIGGERED VIEW SECTION")
        return redirect('view_account', club_id=club_id)
    else:
        print("TRIGGERED CREATE SECTION")
        # Create account page
        Account.objects.create(club=club, balance=0)
        messages.success(
            request, f"Account created successfully for {club.name}.")
        return redirect('club_list')


def view_account(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    account = get_object_or_404(Account, club=club)
    if request.method == 'POST':
        discount_rate = request.POST.get('discount_rate')
        if discount_rate is not None:
            try:
                discount_rate = int(discount_rate)
                if discount_rate >= 0:
                    club.discount_rate = discount_rate
                    club.save()
                    messages.success(
                        request, "Discount rate updated successfully.")
                else:
                    messages.error(
                        request, "Discount rate should be a positive integer.")
            except ValueError:
                messages.error(
                    request, "Discount rate should be a positive integer.")
        else:
            account.delete()
            messages.success(request, "Account deleted successfully.")
        return redirect('club_list')
    else:
        context = {'club': club, 'account': account}
        return render(request, 'UWEFlix/view_account.html', context)


def clubrep_dashboard(request):
    userpermissions = check_permissions(request)
    clubrep = ClubRep.objects.get(user=request.user)
    account = Account.objects.get(club=clubrep.club)

    context = {
        'clubrep': clubrep,
        'account': account,
        'userpermissions': userpermissions,
        'club_id': clubrep.club.id,
    }

    if request.method == 'POST':
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

        price = request.POST.get('amount')

        # Create a new Stripe Checkout Session
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'Account top up',
                        'description': 'Quanity',
                    },
                    'unit_amount': int(price) * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('clubrep_payment_success', args=[clubrep.id, price])
            ),
            cancel_url=request.build_absolute_uri(
                reverse('clubrep_dashboard')),
            **payment_data,
        )

        context = {'session_id': session.id}
        return render(request, 'UWEFlix/payment.html', context)

    return render(request, 'UWEFlix/clubrep_dashboard.html', context)


def clubrep_payment_success(request, clubrep_id, price):
    userpermissions = check_permissions(request)
    clubrep = ClubRep.objects.get(id=clubrep_id)
    account = Account.objects.get(club=clubrep.club)

    # Update the account balance
    account.balance += int(price)
    account.save()

    context = {
        'clubrep': clubrep,
        'account': account,
        'price': price,
        'userpermissions': userpermissions,
        'club_id': clubrep.club.id,
    }

    return render(request, 'UWEFlix/clubrep_payment_success.html', context)
