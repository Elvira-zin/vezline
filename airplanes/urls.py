from django.urls import path
from airplanes.views.airplanes import (
    airplanes_list,
    airplane_create,
    airplane_edit,
    airplane_delete
)

urlpatterns = [
    path("", airplanes_list, name="airplane-list"),
    path("create/", airplane_create, name="airplane-create"),
    path("<int:pk>/edit/", airplane_edit, name="airplane-edit"),
    path("<int:pk>/delete/", airplane_delete, name="airplane-delete"),
]