from django.urls import path, reverse
from Accounts import views

urlpatterns = [
    path('payment/edit/', views.edit_payment_details, name='edit_payment_details'),
    path('clubs/', views.club_list, name='club_list'),
    path('create-account/<int:club_id>/', views.create_or_view_account, name='create_or_view_account'),
    path('view-account/<int:club_id>/', views.view_account, name='view_account'),
    path('clubrep/dashboard/', views.clubrep_dashboard, name='clubrep_dashboard'),
    path('clubrep/payment/success/<int:clubrep_id>/<int:price>/', views.clubrep_payment_success, name='clubrep_payment_success'),
    ]