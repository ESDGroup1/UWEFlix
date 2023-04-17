from django.shortcuts import render, redirect
from django.contrib import messages
from Accounts.forms import PaymentDetailsForm
from Accounts.models import PaymentDetails

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
