from django.urls import path
from Bookings import views

urlpatterns = [
    path('bookings/showing/<int:showing_id>/', views.add_to_cart, name='add_to_cart'),
    # other URL patterns for your app
]

