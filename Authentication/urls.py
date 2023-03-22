from django.urls import path
from Authentication import views

urlpatterns = [
    path("", views.login_view, name="Login"),
    path('register/', views.registration_view, name='registration'),
    ]