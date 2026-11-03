import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.views.decorators.http import require_GET

from bookings.forms.booking import BookingForm
from bookings.models import Booking
from bookings.seat_map import build_seat_map
from flights.models import Flight
from seats.models import Seat


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "booking/booking_list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related(
            "user",
            "flight__departure_airport",
            "flight__arrival_airport",
            "flight__airplane__airline",
            "seat",
            "payment",
        ).order_by("flight__departure_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class SeatMapMixin:
    """
    Adds the chosen flight and its seat map to the booking form page.

    The flight comes from the form: ?flight=<id> on create (see get_initial),
    the booking itself on edit, or the POSTed data when the form has errors.
    """

    def get_flight(self, form):
        flight_id = str(form["flight"].value() or "")
        if not flight_id.isdigit():
            return None
        return Flight.objects.select_related(
            "airplane__airline",
            "departure_airport",
            "arrival_airport",
        ).filter(pk=flight_id).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        flight = self.get_flight(form)
        context["flight"] = flight

        if flight:
            booking = getattr(self, "object", None)
            context["seat_map"] = build_seat_map(
                flight,
                selected_seat_id=form["seat"].value(),
                exclude_booking_id=booking.pk if booking else None,
            )
        else:
            context["upcoming_flights"] = Flight.objects.filter(
                status=Flight.Status.SCHEDULED,
                departure_time__gt=timezone.now(),
            ).select_related(
                "departure_airport",
                "arrival_airport",
            ).order_by("departure_time")[:100]
        return context


class BookingCreateView(LoginRequiredMixin, SeatMapMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "booking/booking_form.html"

    def get_initial(self):
        # "Pick seat" on the home page links here as ?flight=<id>
        initial = super().get_initial()
        flight_id = self.request.GET.get("flight", "")
        if flight_id.isdigit():
            initial["flight"] = flight_id
        return initial

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

        messages.success(
            self.request,
            f"Seat {self.object.seat.number} is yours. Booking {self.object.booking_number} — now the last step: payment.",
        )
        # Step 3 of the flow: pay for the booking that was just made
        return redirect(f"{reverse('payment-create')}?booking={self.object.pk}")


class BookingUpdateView(LoginRequiredMixin, SeatMapMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "booking/booking_form.html"
    success_url = reverse_lazy("booking-list")

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Your seat has been changed.")
        return super().form_valid(form)


class BookingDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "booking/booking_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(
            Booking.objects.select_related(
                "flight__departure_airport",
                "flight__arrival_airport",
                "seat",
            ),
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
        messages.success(request, f"Booking {self.booking.booking_number} has been cancelled.")
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
