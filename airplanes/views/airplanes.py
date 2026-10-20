from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from airplanes.forms.airplanes import AirplaneForm
from airplanes.models import Airplane
from seats.models import Seat


def sync_airplane_seats(airplane, economy_count, business_count, first_class_count):
    existing_numbers = set(
        airplane.seats.values_list("number", flat=True)
    )

    seat_configs = [
        (economy_count, Seat.SeatClass.ECONOMY),
        (business_count, Seat.SeatClass.BUSINESS),
        (first_class_count, Seat.SeatClass.FIRST),
    ]

    letters = "ABCDEF"
    seat_index = 0
    seats_to_create = []

    for count, seat_class in seat_configs:
        for _ in range(count):
            row_number = seat_index // len(letters) + 1
            letter = letters[seat_index % len(letters)]
            seat_number = f"{row_number}{letter}"

            if seat_number not in existing_numbers:
                seats_to_create.append(
                    Seat(
                        airplane=airplane,
                        number=seat_number,
                        seat_class=seat_class,
                    )
                )

            seat_index += 1

    Seat.objects.bulk_create(seats_to_create)

class AirplaneListView(ListView):
    model = Airplane
    template_name = "airplanes/airplanes_list.html"
    context_object_name = "airplanes"

    def get_queryset(self):
        return Airplane.objects.select_related("airline")


class AirplaneCreateView(CreateView):
    model = Airplane
    form_class = AirplaneForm
    template_name = "airplanes/airplane_form.html"
    success_url = reverse_lazy("airplane-list")

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            sync_airplane_seats(
                self.object,
                economy_count=form.cleaned_data["economy_seats"],
                business_count=form.cleaned_data["business_seats"],
                first_class_count=form.cleaned_data["first_class_seats"],
            )

        return response

class AirplaneUpdateView(UpdateView):
    model = Airplane
    form_class = AirplaneForm
    template_name = "airplanes/airplane_form.html"
    success_url = reverse_lazy("airplane-list")

    def form_valid(self, form):
        if self.object.seats.exists():
            form.add_error(
                None,
                "Seat classes cannot be changed after seats have been created.",
            )
            return self.form_invalid(form)

        with transaction.atomic():
            response = super().form_valid(form)

            sync_airplane_seats(
                self.object,
                economy_count=form.cleaned_data["economy_seats"],
                business_count=form.cleaned_data["business_seats"],
                first_class_count=form.cleaned_data["first_class_seats"],
            )

        return response

class AirplaneDeleteView(DeleteView):
    model = Airplane
    template_name = "airplanes/airplane_confirm_delete.html"
    success_url = reverse_lazy("airplane-list")
