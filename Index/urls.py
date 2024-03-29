from django.urls import path
from Index import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('film/<int:film_id>/', views.film_detail_view, name='film_detail'),
    path('allclubs', views.view_all_clubs, name='allclubs'),
    path('logout/', views.logout_view, name="logout"),
    path('test404/', views.error_404, name='test404'),
    path('bookings/', views.purchased_bookings, name='purchased_bookings'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete-account/', views.delete_account, name='delete_account'),
    path('confirm_delete/<int:booking_id>/', views.confirm_delete, name='confirm_delete'),
    path('view-club-bookings/', views.viewclubbookings, name='view_club_bookings'),
    ]

handler404 = 'Index.views.error_404'