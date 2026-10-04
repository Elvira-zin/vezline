from django.urls import path
from seats.views.seats import (
    seats_list,
    seat_create,
    seat_edit,
    seat_delete,
)

urlpatterns = [
    path("", seats_list, name="seat-list"),
    path("create/", seat_create, name="seat-create"),
    path("<int:pk>/edit/", seat_edit, name="seat-edit"),
    path("<int:pk>/delete/", seat_delete, name="seat-delete"),
]