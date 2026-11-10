from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from main.mixins.mixins import StaffRequiredMixin
from seats.forms.seats import SeatForm
from seats.models import Seat


class SeatListView(StaffRequiredMixin, ListView):
    model = Seat
    template_name = "seats/seats_list.html"
    context_object_name = "seats"

    def get_queryset(self):
        return Seat.objects.select_related("airplane__airline")


class SeatCreateView(StaffRequiredMixin, CreateView):
    model = Seat
    form_class = SeatForm
    template_name = "seats/seat_form.html"
    success_url = reverse_lazy("seat-list")


class SeatUpdateView(StaffRequiredMixin, UpdateView):
    model = Seat
    form_class = SeatForm
    template_name = "seats/seat_form.html"
    success_url = reverse_lazy("seat-list")


class SeatDeleteView(StaffRequiredMixin, DeleteView):
    model = Seat
    template_name = "seats/seat_confirm_delete.html"
    context_object_name = "seat"
    success_url = reverse_lazy("seat-list")