from django.urls import path
from Accounts import views

urlpatterns = [
    path('payment/edit/', views.edit_payment_details, name='edit_payment_details')
    ]