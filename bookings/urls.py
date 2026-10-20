from django.urls import path

from bookings.views.booking import (
    BookingListView,
    BookingCreateView,
    BookingUpdateView,
    BookingDeleteView,
    flight_seats,
)

urlpatterns = [
    path("", BookingListView.as_view(), name="booking-list"),
    path("create/", BookingCreateView.as_view(), name="booking-create"),
    path("<int:pk>/edit/", BookingUpdateView.as_view(), name="booking-edit"),
    path("<int:pk>/delete/", BookingDeleteView.as_view(), name="booking-delete"),
    path(
        "flights/<int:flight_id>/seats/",
        flight_seats,
        name="flight-seats",
    ),
]