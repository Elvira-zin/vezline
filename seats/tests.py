import importlib

from django.apps import apps
from django.core.exceptions import ValidationError
from django.test import TestCase

from airlines.models import Airline
from airplanes.models import Airplane
from airplanes.views.airplanes import sync_airplane_seats
from seats.models import Seat


class SeatTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        airline = Airline.objects.create(name="Vezline Air", code="VZ", country="Poland")
        # 14 seats -> rows 1-3 (6 seats per row)
        cls.plane = Airplane.objects.create(airline=airline, model="A220", registration_number="SP-SEA", capacity=14)

    def test_row_and_letter_is_valid(self):
        seat = Seat(airplane=self.plane, number=" 3c ")
        seat.full_clean()

        self.assertEqual(seat.number, "3C")

    def test_digits_only_is_rejected(self):
        with self.assertRaises(ValidationError):
            Seat(airplane=self.plane, number="12").full_clean()

    def test_row_outside_airplane_is_rejected(self):
        with self.assertRaises(ValidationError):
            Seat(airplane=self.plane, number="4A").full_clean()

    def test_premium_classes_get_front_rows(self):
        sync_airplane_seats(self.plane, economy_count=8, business_count=4, first_class_count=2)

        classes = dict(Seat.objects.filter(airplane=self.plane).values_list("number", "seat_class"))
        self.assertEqual(classes["1A"], Seat.SeatClass.FIRST)
        self.assertEqual(classes["1C"], Seat.SeatClass.BUSINESS)
        self.assertEqual(classes["3B"], Seat.SeatClass.ECONOMY)

    def test_migration_moves_business_from_back_to_front(self):
        # How the old code did it: economy first, business at the back
        for number, seat_class in [("1A", "ECONOMY"), ("1B", "ECONOMY"), ("2A", "BUSINESS")]:
            Seat.objects.create(airplane=self.plane, number=number, seat_class=seat_class)

        migration = importlib.import_module("seats.migrations.0004_move_premium_classes_to_front")
        migration.move_premium_classes_to_front(apps, schema_editor=None)

        classes = dict(Seat.objects.filter(airplane=self.plane).values_list("number", "seat_class"))
        self.assertEqual(classes, {"1A": "BUSINESS", "1B": "ECONOMY", "2A": "ECONOMY"})
