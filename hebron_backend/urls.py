from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/", include("leads.urls")),
    path("", admin.site.urls),
]