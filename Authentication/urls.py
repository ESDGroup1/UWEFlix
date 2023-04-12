from django.urls import path
from Authentication import views

urlpatterns = [
    path("", views.login_view, name="Login"),
    path('register/', views.registration_view, name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('login/guest/', views.login_guest_view, name='login_guest'),
    ]