from datetime import datetime, timedelta
from django.utils import timezone
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
from .models import Account, ClubRep, Club, ClubReceipt, PersonalReceipt, Statement, Receipt
from django.db.models import Q
from dateutil.relativedelta import relativedelta

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

    ClubReceipt.objects.create(
        account=account,
        price=price,
        datetime=datetime.now(),
    )
    

    return render(request, 'UWEFlix/clubrep_payment_success.html', context)

def create_monthly_statements():
    # Get the date of the first day of the current month
    today = timezone.now().date()
    first_day_of_month = datetime(today.year, today.month, 1).date()

    # Get the start and end dates of the previous month
    end_of_last_month = first_day_of_month - timedelta(days=1)
    start_of_last_month = datetime(end_of_last_month.year, end_of_last_month.month, 1).date()

    # Create a statement for each account
    accounts = Account.objects.all()
    for account in accounts:
        # Check if a statement for this account and dates already exists
        if Statement.objects.filter(
            Q(account=account) & Q(startdate=start_of_last_month) & Q(enddate=end_of_last_month)
        ).exists():
            continue

        # Create a new statement for this account and dates
        statement = Statement.objects.create(
            account=account,
            startdate=start_of_last_month,
            enddate=end_of_last_month
        )

def statement_list(request):
    create_monthly_statements() # Create new statements every time the page is accessed
    
    today = datetime.now().date()
    first_day_of_month = datetime(today.year, today.month, 1).date()
    end_of_last_month = first_day_of_month - timedelta(days=1)
    start_of_last_month = datetime(end_of_last_month.year, end_of_last_month.month, 1).date()

    statements = Statement.objects.filter(startdate=start_of_last_month, enddate=end_of_last_month)
    
    context = {'statements': statements}
    return render(request, 'UWEFlix/statement_list.html', context)


def statement_detail(request, statement_id):
    statement = get_object_or_404(Statement, pk=statement_id)
    account = statement.account
    receipts = Receipt.objects.filter(account=account, date__range=[statement.startdate, statement.enddate])
    club_receipts = ClubReceipt.objects.filter(account=account, datetime__range=[statement.startdate, statement.enddate])
    
    context = {'statement': statement, 'receipts': receipts, 'club_receipts': club_receipts}
    return render(request, 'UWEFlix/statement_detail.html', context)

def club_account(request):
    clubrep = get_object_or_404(ClubRep, user=request.user)
    account = Account.objects.get(club=clubrep.club)
    
    # Get the start and end dates of the current month
    today = timezone.now().date()
    first_day_of_month = datetime(today.year, today.month, 1).date()
    end_of_month = first_day_of_month + relativedelta(months=1, days=-1)

    # Filter receipts and club receipts by the current month
    receipts = Receipt.objects.filter(
        account=account,
        date__range=[first_day_of_month, end_of_month]
    )
    club_receipts = ClubReceipt.objects.filter(
        account=account,
        datetime__range=[first_day_of_month, end_of_month]
    )
    
    context = {'receipts': receipts, 'club_receipts': club_receipts}
    return render(request, 'UWEFlix/club_account.html', context)

def personal_receipts(request):
    receipts = PersonalReceipt.objects.filter(user=request.user)
    context = {'receipts': receipts}
    return render(request, 'UWEFlix/personal_receipts.html', context)