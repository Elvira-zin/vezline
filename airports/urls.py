from django.urls import path
from airports.views.airports import airport_edit, airport_create, airports_list, airport_delete

urlpatterns = [
    path("", airports_list, name="airport-list"),
    path("create/", airport_create, name="airport-create"),
    path("<int:pk>/edit/", airport_edit, name="airport-edit"),
    path("<int:pk>/delete/", airport_delete, name="airport-delete"),
]