from django.urls import path
from CinManager import views

urlpatterns = [
    path('addfilm/', views.add_film_view, name='addfilm'),
    path("addmanager/", views.addCinManagers, name="addcinman"),
    path("createclub/", views.create_club_view, name="createclub"),
    path("createscreen/", views.create_screen_view, name="createscreen"),
    path("createshowing/", views.create_showing_view, name="createshowing"),
    path('film/<int:film_id>/delete/', views.delete_film, name='delete_film'),
    path('updatefilm/<int:film_id>', views.update_film, name='update_film'),
    path('updateclub/<int:club_id>', views.update_club, name='update_club'),
    path('club/<int:club_id>/update/', views.update_club_rep, name='update_club_rep'),
    path('clubcreatedsucess/<str:username>/<str:password>/', views.clubcreatedsucess, name='clubcreatedsucess'),
    path('delete-requests/', views.delete_request_list, name='delete_request_list'),
    path('delete-request/<int:deleteRequest_id>/', views.deleteRequests, name='delete_request'),
    path('deny-delete-request/<int:deleteRequest_id>/', views.denyrequest, name='deny_delete_request'),
    ]