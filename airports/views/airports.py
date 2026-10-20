from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from airports.forms.forms import AirportForm
from airports.models import Airport


class AirportListView(ListView):
    model = Airport
    template_name = "airports/airports_list.html"
    context_object_name = "airports"


class AirportCreateView(CreateView):
    model = Airport
    form_class = AirportForm
    template_name = "airports/airport_form.html"
    success_url = reverse_lazy("airport-list")


class AirportUpdateView(UpdateView):
    model = Airport
    form_class = AirportForm
    template_name = "airports/airport_form.html"
    success_url = reverse_lazy("airport-list")


class AirportDeleteView(DeleteView):
    model = Airport
    template_name = "airports/airport_confirm_delete.html"
    context_object_name = "airport"
    success_url = reverse_lazy("airport-list")