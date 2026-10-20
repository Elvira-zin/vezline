import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.views.decorators.http import require_GET

from bookings.forms.booking import BookingForm
from bookings.models import Booking
from flights.models import Flight
from seats.models import Seat


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "booking/booking_list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related("user", "flight", "seat")


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "booking/booking_form.html"
    success_url = reverse_lazy("booking-list")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.user = self.request.user
                self.object.booking_number = uuid.uuid4().hex[:8].upper()
                self.object.save()
        except IntegrityError:
            form.add_error(
                "seat",
                "This seat is already booked for this flight.",
            )
            return self.form_invalid(form)

        return redirect(self.get_success_url())


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "booking/booking_form.html"
    success_url = reverse_lazy("booking-list")

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "booking/booking_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(
            Booking,
            pk=kwargs["pk"],
            user=request.user,
        )

        if self.booking.status == Booking.Status.CANCELLED:
            return redirect("booking-list")

        if self.booking.flight.departure_time <= timezone.now():
            messages.error(
                request,
                "You cannot cancel a booking after the flight has departed.",
            )
            return redirect("booking-list")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = self.booking
        return context

    def post(self, request, *args, **kwargs):
        self.booking.status = Booking.Status.CANCELLED
        self.booking.save(update_fields=["status"])
        return redirect("booking-list")


@require_GET
def flight_seats(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)

    seats = sorted(
        Seat.objects.filter(airplane_id=flight.airplane_id),
        key=lambda seat: int(seat.number)
        if seat.number.isdigit()
        else float("inf"),
    )

    return JsonResponse({
        "seats": [
            {
                "id": seat.id,
                "number": seat.number,
                "seat_class": seat.get_seat_class_display(),
            }
            for seat in seats
        ]
    })