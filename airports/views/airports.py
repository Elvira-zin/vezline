from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from airports.forms.forms import AirportForm
from airports.models import Airport
from main.mixins.mixins import StaffRequiredMixin


class AirportListView(StaffRequiredMixin, ListView):
    model = Airport
    template_name = "airports/airports_list.html"
    context_object_name = "airports"


class AirportCreateView(StaffRequiredMixin, CreateView):
    model = Airport
    form_class = AirportForm
    template_name = "airports/airport_form.html"
    success_url = reverse_lazy("airport-list")


class AirportUpdateView(StaffRequiredMixin, UpdateView):
    model = Airport
    form_class = AirportForm
    template_name = "airports/airport_form.html"
    success_url = reverse_lazy("airport-list")


class AirportDeleteView(StaffRequiredMixin, DeleteView):
    model = Airport
    template_name = "airports/airport_confirm_delete.html"
    context_object_name = "airport"
    success_url = reverse_lazy("airport-list")