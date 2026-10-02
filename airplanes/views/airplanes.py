from django.shortcuts import render, get_object_or_404, redirect

from airplanes.forms.airplanes import AirplaneForm
from airplanes.models import Airplane


def airplane_list(request):
    airplanes = Airplane.objects.all()
    return render(request, "airplanes/airplanes_list.html", {"airplanes": airplanes})

def airplane_create(request):
    if request.method == "POST":
        form = AirplaneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("airplanes_list")
    else:
        form = AirplaneForm()
    return render(request, "airplanes/airplane_form.html", {"form": form})

def airplane_edit(request, pk):
    airplane = get_object_or_404(Airplane, pk=pk)

    if request.method == "POST":
        form = AirplaneForm(request.POST, instance=airplane)

        if form.is_valid():
            form.save()
            return redirect("airplanes_list")
    else:
        form = AirplaneForm(instance=airplane)

    return render(
        request, "airplanes/airplane_form.html",
        {"form": form}
    )

def airplane_delete(request, pk):
    airplane = get_object_or_404(Airplane, pk=pk)

    if request.method == "POST":
        airplane.delete()
        return redirect("airplanes_list")

    return render(
        request,
        "airplanes/airplane_confirm_delete.html",
        {"airplane": airplane}
    )