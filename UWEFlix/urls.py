from django.urls import path
from UWEFlix import views

urlpatterns = [
    path("", views.login_view, name="Login"),
    path('register/', views.registration_view, name='registration'),
    path('home/', views.home, name='home'),
    path('addfilm/', views.add_film_view, name='addfilm'),
    path("logout/", views.logout_view, name="logout"),
    path("addmanager/", views.addCinManagers, name="addcinman"),
    path("createclub/", views.create_club_view, name="createclub"),
    path("createscreen/", views.create_screen_view, name="createscreen"),
    path("createshowing/", views.create_showing_view, name="createshowing"),
    path('film/<int:film_id>/', views.film_detail_view, name='film_detail'),
    path('film/<int:film_id>/delete/', views.delete_film, name='delete_film'),
    path('updatefilm/<int:film_id>', views.update_film, name='update_film'),
    path('updateclub/<int:club_id>', views.update_club, name='update_club'),
    path('allclubs', views.view_all_clubs, name='allclubs'),
    path('clubcreatedsucess/<str:username>/<str:password>/', views.clubcreatedsucess, name='clubcreatedsucess'),
    ]