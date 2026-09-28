from django.urls import path
from airlines.views.airlines import airlines_list, airline_create, airline_edit, airline_delete

urlpatterns = [
    path("", airlines_list, name="airline-list"),
    path("create/", airline_create, name="airline-create"),
    path("<int:pk>/edit/", airline_edit, name="airline-edit"),
    path("<int:pk>/delete/", airline_delete, name="airline-delete"),
]