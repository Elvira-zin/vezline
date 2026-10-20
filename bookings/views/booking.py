import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET

from bookings.forms.booking import BookingForm
from bookings.models import Booking
from flights.models import Flight
from seats.models import Seat


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).select_related("user", "flight", "seat")
    return render(request, "booking/booking_list.html", {"bookings": bookings})

@login_required
def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.booking_number = uuid.uuid4().hex[:8].upper()
                    booking.save()

                return redirect("booking-list")

            except IntegrityError:
                form.add_error(
                    "seat",
                    "This seat is already booked for this flight.",
                )
    else:
        form = BookingForm()

    return render(request, "booking/booking_form.html", {"form": form})

@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():
            form.save()
            return redirect("booking-list")
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "booking/booking_form.html",
        {"form": form}
    )

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
        user=request.user,
    )

    if booking.status == Booking.Status.CANCELLED:
        return redirect("booking-list")

    if booking.flight.departure_time <= timezone.now():
        messages.error(
            request,
            "You cannot cancel a booking after the flight has departed."
        )
        return redirect("booking-list")

    if request.method == "POST":
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])
        return redirect("booking-list")

    return render(
        request,
        "booking/booking_confirm_delete.html",
        {"booking": booking}
    )

@login_required
@require_GET
def flight_seats(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)

    seats = sorted(
        Seat.objects.filter(airplane_id=flight.airplane_id),
        key=lambda seat: int(seat.number) if seat.number.isdigit() else float("inf"),
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