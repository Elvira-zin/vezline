from bookings.models import Booking
from seats.models import Seat
from seats.models.seat import SEAT_NUMBER

LEFT_LETTERS = "ABC"
RIGHT_LETTERS = "DEF"


def build_seat_map(flight, selected_seat_id=None, exclude_booking_id=None):
    """
    Seat map of the flight's airplane.

    exclude_booking_id: when a booking is being edited, its own seat
    must not be shown as taken.
    """
    taken_ids = set(
        Booking.objects.filter(
            flight=flight,
            status=Booking.Status.CONFIRMED,
            seat__isnull=False,
        )
        .exclude(pk=exclude_booking_id)
        .values_list("seat_id", flat=True)
    )
    seats = Seat.objects.filter(airplane_id=flight.airplane_id)
    return group_seats(seats, taken_ids, selected_seat_id)


def group_seats(seats, taken_ids, selected_seat_id=None):
    """
    Group seats into cabin rows for the template.

    Returns a dict:
        rows:  [{"number": 12, "left": [cell, cell, cell], "right": [...],
                 "class_start": "BUSINESS" or ""}]
               a missing seat in a row is None, so the columns stay aligned
        other: cells whose number is not like "12C" (old digit-only seats)
        selected: the chosen cell or None
        free / total: seat counts
    """
    selected = str(selected_seat_id or "")
    rows = {}
    other = []
    free = total = 0
    selected_cell = None

    for seat in seats:
        cell = {
            "id": seat.id,
            "number": seat.number,
            "seat_class": seat.seat_class,
            "taken": seat.id in taken_ids,
            "selected": str(seat.id) == selected,
        }
        total += 1
        if cell["selected"]:
            selected_cell = cell
        if not cell["taken"]:
            free += 1

        match = SEAT_NUMBER.match(seat.number)
        if match:
            cell["letter"] = match["letter"]
            rows.setdefault(int(match["row"]), {})[match["letter"]] = cell
        else:
            cell["letter"] = seat.number
            other.append(cell)

    cabin = []
    previous_class = None
    for number, letters in sorted(rows.items()):
        row = {
            "number": number,
            "left": [letters.get(letter) for letter in LEFT_LETTERS],
            "right": [letters.get(letter) for letter in RIGHT_LETTERS],
        }
        row_class = next(cell["seat_class"] for cell in letters.values())
        row["class_start"] = row_class if row_class != previous_class else ""
        previous_class = row_class
        cabin.append(row)

    other.sort(key=lambda cell: (len(cell["number"]), cell["number"]))

    return {
        "rows": cabin,
        "other": other,
        "selected": selected_cell,
        "free": free,
        "total": total,
    }
