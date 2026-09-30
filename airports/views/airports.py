from django.shortcuts import render, redirect, get_object_or_404

from airports.forms.forms import AirportForm
from airports.models import Airport


def airports_list(request):
    airports = Airport.objects.all()

    return render(
        request,
        "airports/airports_list.html",
        {"airports": airports},
    )

def airport_create(request):
    if request.method == "POST":
        form = AirportForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("airport-list")
    else:
        form = AirportForm()

    return render(
        request,
        "airports/airport_form.html",
        {"form": form},
    )

def airport_edit(request, pk):
    airport = get_object_or_404(Airport, pk=pk)

    if request.method == "POST":
        form = AirportForm(request.POST, instance=airport)

        if form.is_valid():
            form.save()
            return redirect("airport-list")
    else:
        form = AirportForm(instance=airport)

    return render(
        request,
        "airports/airport_form.html",
        {"form": form},
    )

def airport_delete(request, pk):
    airport = get_object_or_404(Airport, pk=pk)

    if request.method == "POST":
        airport.delete()
        return redirect("airport-list")

    return render(
        request,
        "airports/airport_confirm_delete.html",
        {"airport": airport},
    )