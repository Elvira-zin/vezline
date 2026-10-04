from django.urls import path
from bookings.views.booking import (
    booking_list,
    booking_create,
    booking_edit,
    booking_delete,
)

urlpatterns = [
    path("", booking_list, name="booking-list"),
    path("create/", booking_create, name="booking-create"),
    path("<int:pk>/edit/", booking_edit, name="booking-edit"),
    path("<int:pk>/delete/", booking_delete, name="booking-delete"),
]