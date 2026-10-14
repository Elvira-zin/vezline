import uuid

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from bookings.forms.booking import BookingForm
from bookings.models import Booking

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "booking/booking_list.html", {"bookings": bookings})

@login_required
def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.booking_number = uuid.uuid4().hex[:8].upper()
            booking.save()
            return redirect("booking-list")
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

    if request.method == "POST":
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])
        return redirect("booking-list")

    return render(
        request,
        "booking/booking_confirm_delete.html",
        {"booking": booking}
    )