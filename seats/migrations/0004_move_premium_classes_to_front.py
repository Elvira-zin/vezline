import re
from collections import Counter

from django.db import migrations

# Order of classes from the front of the plane to the back
CLASS_ORDER = ["FIRST", "BUSINESS", "ECONOMY"]
SEAT_NUMBER = re.compile(r"^(\d+)([A-Z]*)$")


def seat_position(seat):
    """Sort key: row number, then letter. "12C" -> (12, "C")."""
    match = SEAT_NUMBER.match(seat.number)
    if not match:
        return (10**6, seat.number)
    return (int(match[1]), match[2])


def move_premium_classes_to_front(apps, schema_editor):
    """
    Old sync_airplane_seats put economy in the first rows and business at the back.
    Keep how many seats each class has, but give the front rows to first and business.
    """
    Seat = apps.get_model("seats", "Seat")
    airplane_ids = Seat.objects.values_list("airplane_id", flat=True).distinct()

    for airplane_id in airplane_ids:
        seats = sorted(Seat.objects.filter(airplane_id=airplane_id), key=seat_position)
        counts = Counter(seat.seat_class for seat in seats)
        new_classes = [seat_class for seat_class in CLASS_ORDER for _ in range(counts[seat_class])]

        changed = []
        for seat, new_class in zip(seats, new_classes):
            if seat.seat_class != new_class:
                seat.seat_class = new_class
                changed.append(seat)
        Seat.objects.bulk_update(changed, ["seat_class"])


class Migration(migrations.Migration):

    dependencies = [
        ("seats", "0003_seat_unique_seats_in_airplane"),
    ]

    operations = [
        migrations.RunPython(move_premium_classes_to_front, migrations.RunPython.noop),
    ]
