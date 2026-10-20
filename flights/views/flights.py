from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from flights.forms.flights import FlightForm
from flights.models import Flight


class FlightListView(ListView):
    model = Flight
    template_name = "flights/flights_list.html"
    context_object_name = "flights"

    def get_queryset(self):
        return Flight.objects.select_related(
            "airplane__airline",
            "departure_airport",
            "arrival_airport",
        )


class FlightCreateView(CreateView):
    model = Flight
    form_class = FlightForm
    template_name = "flights/flight_form.html"
    success_url = reverse_lazy("flight-list")


class FlightUpdateView(UpdateView):
    model = Flight
    form_class = FlightForm
    template_name = "flights/flight_form.html"
    success_url = reverse_lazy("flight-list")


class FlightDeleteView(DeleteView):
    model = Flight
    template_name = "flights/flight_confirm_delete.html"
    context_object_name = "flight"
    success_url = reverse_lazy("flight-list")
