from django.urls import path

from seats.views.seats import (
    SeatListView,
    SeatCreateView,
    SeatUpdateView,
    SeatDeleteView,
)

urlpatterns = [
    path("", SeatListView.as_view(), name="seat-list"),
    path("create/", SeatCreateView.as_view(), name="seat-create"),
    path("<int:pk>/edit/", SeatUpdateView.as_view(), name="seat-edit"),
    path("<int:pk>/delete/", SeatDeleteView.as_view(), name="seat-delete"),
]