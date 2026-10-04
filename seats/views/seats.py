from django.shortcuts import render, redirect, get_object_or_404

from seats.forms.seats import SeatForm
from seats.models import Seat


def seats_list(request):
    seats = Seat.objects.all()
    return render(request, "seats/seats_list.html", {"seats": seats})

def seat_create(request):
    if request.method == "POST":
        form = SeatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("seat-list")
    else:
        form = SeatForm()
    return render(request, "seats/seat_form.html", {"form": form})

def seat_edit(request, pk):
    seat = get_object_or_404(Seat, pk=pk)

    if request.method == "POST":
        form = SeatForm(request.POST, instance=seat)

        if form.is_valid():
            form.save()
            return redirect("seat-list")
    else:
        form = SeatForm(instance=seat)

    return render(
        request,
        "seats/seat_form.html",
        {"form": form},
    )

def seat_delete(request, pk):
    seat = get_object_or_404(Seat, pk=pk)

    if request.method == "POST":
        seat.delete()
        return redirect("seat-list")

    return render(
        request,
        "seats/seat_confirm_delete.html",
        {"seat": seat},
    )
