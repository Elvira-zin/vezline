from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from airlines.forms.airlines import AirlineForm
from airlines.models import Airline
from main.mixins.mixins import StaffRequiredMixin


class AirlineListView(StaffRequiredMixin, ListView):
    model = Airline
    template_name = "airlines/airlines_list.html"
    context_object_name = "airlines"


class AirlineCreateView(StaffRequiredMixin, CreateView):
    model = Airline
    form_class = AirlineForm
    template_name = "airlines/airline_form.html"
    success_url = reverse_lazy("airline-list")


class AirlineUpdateView(StaffRequiredMixin, UpdateView):
    model = Airline
    form_class = AirlineForm
    template_name = "airlines/airline_form.html"
    success_url = reverse_lazy("airline-list")


class AirlineDeleteView(StaffRequiredMixin, DeleteView):
    model = Airline
    template_name = "airlines/airline_confirm_delete.html"
    success_url = reverse_lazy("airline-list")