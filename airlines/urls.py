from django.urls import path

from airlines.views.airlines import (
    AirlineListView,
    AirlineCreateView,
    AirlineUpdateView,
    AirlineDeleteView,
)

urlpatterns = [
    path("", AirlineListView.as_view(), name="airline-list"),
    path("create/", AirlineCreateView.as_view(), name="airline-create"),
    path("<int:pk>/edit/", AirlineUpdateView.as_view(), name="airline-edit"),
    path("<int:pk>/delete/", AirlineDeleteView.as_view(), name="airline-delete"),
]