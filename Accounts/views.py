from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from Accounts.forms import PaymentDetailsForm
from Accounts.models import PaymentDetails
from django.shortcuts import render
from django.shortcuts import render
from django.views.generic import ListView
from django.urls import reverse_lazy

from .models import Club, Account

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
    payment_details, created = PaymentDetails.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # update the payment details object with the new form data
        payment_details_form = PaymentDetailsForm(request.POST, instance=payment_details)
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

    context = {'payment_details_form': payment_details_form, 'userpermissions': userpermissions}
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
        messages.success(request, f"Account created successfully for {club.name}.")
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
                    messages.success(request, "Discount rate updated successfully.")
                else:
                    messages.error(request, "Discount rate should be a positive integer.")
            except ValueError:
                messages.error(request, "Discount rate should be a positive integer.")
        else:
            account.delete()
            messages.success(request, "Account deleted successfully.")
        return redirect('club_list')
    else:
        context = {'club': club, 'account': account}
        return render(request, 'UWEFlix/view_account.html', context)



