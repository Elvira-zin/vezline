from django.shortcuts import render, get_object_or_404, redirect

from airplanes.forms.airplanes import AirplaneForm
from airplanes.models import Airplane
from seats.models import Seat


def sync_airplane_seats(airplane, economy_count, business_count, first_class_count):
    existing_numbers = set(
        airplane.seats.values_list("number", flat=True)
    )

    seat_configs = [
        (economy_count, Seat.SeatClass.ECONOMY),
        (business_count, Seat.SeatClass.BUSINESS),
        (first_class_count, Seat.SeatClass.FIRST),
    ]

    letters = "ABCDEF"
    seat_index = 0
    seats_to_create = []

    for count, seat_class in seat_configs:
        for _ in range(count):
            row_number = seat_index // len(letters) + 1
            letter = letters[seat_index % len(letters)]
            seat_number = f"{row_number}{letter}"

            if seat_number not in existing_numbers:
                seats_to_create.append(
                    Seat(
                        airplane=airplane,
                        number=seat_number,
                        seat_class=seat_class,
                    )
                )

            seat_index += 1

    Seat.objects.bulk_create(seats_to_create)

def airplanes_list(request):
    airplanes = Airplane.objects.select_related("airline")
    return render(request, "airplanes/airplanes_list.html", {"airplanes": airplanes})

def airplane_create(request):
    if request.method == "POST":
        form = AirplaneForm(request.POST)
        if form.is_valid():
            airplane = form.save()

            sync_airplane_seats(
                airplane,
                economy_count=form.cleaned_data["economy_seats"],
                business_count=form.cleaned_data["business_seats"],
                first_class_count=form.cleaned_data["first_class_seats"],
            )

            return redirect("airplane-list")
    else:
        form = AirplaneForm()
    return render(request, "airplanes/airplane_form.html", {"form": form})

def airplane_edit(request, pk):
    airplane = get_object_or_404(Airplane, pk=pk)

    if request.method == "POST":
        form = AirplaneForm(request.POST, instance=airplane)

        if form.is_valid():
            economy_count = form.cleaned_data["economy_seats"]
            business_count = form.cleaned_data["business_seats"]
            first_class_count = form.cleaned_data["first_class_seats"]

            existing_seats = airplane.seats.all()

            if existing_seats.exists():
                form.add_error(
                    None,
                    "Seat classes cannot be changed after seats have been created."
                )
            else:
                airplane = form.save()

                sync_airplane_seats(
                    airplane,
                    economy_count=economy_count,
                    business_count=business_count,
                    first_class_count=first_class_count,
                )

                return redirect("airplane-list")
    else:
        form = AirplaneForm(instance=airplane)

    return render(
        request,
        "airplanes/airplane_form.html",
        {"form": form},
    )

def airplane_delete(request, pk):
    airplane = get_object_or_404(Airplane, pk=pk)

    if request.method == "POST":
        airplane.delete()
        return redirect("airplane-list")

    return render(
        request,
        "airplanes/airplane_confirm_delete.html",
        {"airplane": airplane}
    )