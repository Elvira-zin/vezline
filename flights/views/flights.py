from django.shortcuts import get_object_or_404, redirect, render

from flights.forms.flights import FlightForm
from flights.models import Flight


def flight_list(request):
    flights = Flight.objects.all()
    return render(request, "flights/flights_list.html", {"flights": flights})

def flight_create(request):
    if request.method == "POST":
        form = FlightForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("flight-list")
    else:
        form = FlightForm()

    return render(
        request,
        "flights/flight_form.html",
        {"form": form},
    )


def flight_edit(request, pk):
    flight = get_object_or_404(Flight, pk=pk)

    if request.method == "POST":
        form = FlightForm(request.POST, instance=flight)

        if form.is_valid():
            form.save()
            return redirect("flight-list")
    else:
        form = FlightForm(instance=flight)

    return render(
        request,
        "flights/flight_form.html",
        {"form": form},
    )


def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)

    if request.method == "POST":
        flight.delete()
        return redirect("flight-list")

    return render(
        request,
        "flights/flight_confirm_delete.html",
        {"flight": flight},
    )
