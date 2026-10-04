from django.urls import path

from flights.views.flights import (
    flight_create,
    flight_delete,
    flight_edit,
    flight_list,
)

urlpatterns = [
    path("", flight_list, name="flight-list"),
    path("create/", flight_create, name="flight-create"),
    path("<int:pk>/edit/", flight_edit, name="flight-edit"),
    path("<int:pk>/delete/", flight_delete, name="flight-delete"),
]