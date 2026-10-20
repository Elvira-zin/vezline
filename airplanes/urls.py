from django.urls import path
from airplanes.views.airplanes import (
    AirplaneListView,
    AirplaneCreateView,
    AirplaneUpdateView,
    AirplaneDeleteView,
)

urlpatterns = [
    path("", AirplaneListView.as_view(), name="airplane-list"),
    path("create/", AirplaneCreateView.as_view(), name="airplane-create"),
    path("<int:pk>/edit/", AirplaneUpdateView.as_view(), name="airplane-edit"),
    path("<int:pk>/delete/", AirplaneDeleteView.as_view(), name="airplane-delete"),
]