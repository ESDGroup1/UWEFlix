from django.urls import path
from Index import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('film/<int:film_id>/', views.film_detail_view, name='film_detail'),
    path('allclubs', views.view_all_clubs, name='allclubs'),
    path('logout/', views.logout_view, name="logout"),
    path('test404/', views.error_404, name='test404')
    ]

handler404 = 'Index.views.error_404'