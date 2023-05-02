from django.urls import path
from Bookings import views

urlpatterns = [
    path('bookings/showing/<int:showing_id>/', views.add_to_cart, name='add_to_cart'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('payment/success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('clubrep_payment/<int:booking_id>/', views.clubrep_payment, name='clubrep_payment'),
]

