from django.shortcuts import render, redirect, get_object_or_404

from airlines.forms.airlines import AirlineForm
from airlines.models import Airline



def airlines_list(request):
    airlines = Airline.objects.all()
    return render(request, "airlines/airlines_list.html", {"airlines": airlines, "test": "Train"},)


def airline_create(request):
    if request.method == "POST":
        form = AirlineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("airline-list")
    else:
        form = AirlineForm()
    return render(request, "airlines/airline_form.html", {"form": form}, )

def airline_edit(request, pk):
    airline = get_object_or_404(Airline, pk=pk)

    if request.method == "POST":
        form = AirlineForm(request.POST, request.FILES, instance=airline)

        if form.is_valid():
            form.save()
            return redirect("airline-list")
    else:
        form = AirlineForm(instance=airline)

    return render(
        request,
        "airlines/airline_form.html",
        {"form": form},
    )

def airline_delete(request, pk):
    airline = get_object_or_404(Airline, pk=pk)

    if request.method == "POST":
        airline.delete()
        return redirect("airline-list")

    return render(
        request,
        "airlines/airline_confirm_delete.html",
        {"airline": airline},
    )
