from django.urls import path

from airports.views.airports import (
    AirportListView,
    AirportCreateView,
    AirportUpdateView,
    AirportDeleteView,
)

urlpatterns = [
    path("", AirportListView.as_view(), name="airport-list"),
    path("create/", AirportCreateView.as_view(), name="airport-create"),
    path("<int:pk>/edit/", AirportUpdateView.as_view(), name="airport-edit"),
    path("<int:pk>/delete/", AirportDeleteView.as_view(), name="airport-delete"),
]