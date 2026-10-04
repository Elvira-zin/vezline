import uuid

from django.shortcuts import render, redirect, get_object_or_404

from bookings.forms.booking import BookingForm
from bookings.models import Booking

def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, "booking/booking_list.html", {"bookings": bookings})

def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.booking_number = uuid.uuid4().hex[:8].upper()
            booking.save()
            return redirect("booking-list")
    else:
        form = BookingForm()
    return render(request, "booking/booking_form.html", {"form": form})

def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

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

def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "POST":
        booking.delete()
        return redirect("booking-list")

    return render(
        request,
        "booking/booking_confirm_delete.html",
        {"booking": booking}
    )