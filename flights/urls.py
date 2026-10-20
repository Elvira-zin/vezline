from django.urls import path

from flights.views.flights import (
    FlightListView,
    FlightCreateView,
    FlightUpdateView,
    FlightDeleteView,
)

urlpatterns = [
    path("", FlightListView.as_view(), name="flight-list"),
    path("create/", FlightCreateView.as_view(), name="flight-create"),
    path("<int:pk>/edit/", FlightUpdateView.as_view(), name="flight-edit"),
    path("<int:pk>/delete/", FlightDeleteView.as_view(), name="flight-delete"),
]