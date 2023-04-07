
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("Authentication.urls")),
    path("cinmanager/", include("CinManager.urls")),
    path("index/", include("Index.urls")),
    path("bookings/", include("Bookings.urls")),
    path('admin/', admin.site.urls),
]

handler404 = 'Index.views.error_404'
urlpatterns += staticfiles_urlpatterns()
