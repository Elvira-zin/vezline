from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from airlines.models import Airline
from airplanes.models import Airplane
from airports.models import Airport
from bookings.models import Booking
from flights.models import Flight
from main.views import with_seat_stats
from seats.models import Seat
from users.models import User


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gdn = Airport.objects.create(name="Lech Wałęsa", code="GDN", city="Gdańsk", country="Poland")
        cls.waw = Airport.objects.create(name="Chopin", code="WAW", city="Warsaw", country="Poland")
        airline = Airline.objects.create(name="Vezline Air", code="VZ", country="Poland")
        cls.plane = Airplane.objects.create(
            airline=airline, model="A220", registration_number="SP-TST", capacity=4,
        )
        cls.seats = [
            Seat.objects.create(airplane=cls.plane, number="1", seat_class=Seat.SeatClass.BUSINESS),
            Seat.objects.create(airplane=cls.plane, number="2"),
            Seat.objects.create(airplane=cls.plane, number="3"),
            Seat.objects.create(airplane=cls.plane, number="4"),
        ]
        departure = timezone.now() + timedelta(days=2)
        cls.flight = Flight.objects.create(
            airplane=cls.plane,
            departure_airport=cls.gdn,
            arrival_airport=cls.waw,
            flight_number="VZ100",
            departure_time=departure,
            arrival_time=departure + timedelta(hours=1),
            price="189.00",
        )
        cls.user = User.objects.create_user(email="test@vezline.dev", password="test-pass-123")
        Booking.objects.create(user=cls.user, flight=cls.flight, seat=cls.seats[1], booking_number="T1")
        Booking.objects.create(
            user=cls.user, flight=cls.flight, seat=cls.seats[2], booking_number="T2",
            status=Booking.Status.CANCELLED,
        )

    def test_seat_stats_count_only_confirmed_bookings(self):
        flight = with_seat_stats(Flight.objects.all()).get(pk=self.flight.pk)

        self.assertEqual(flight.seats_total, 4)
        self.assertEqual(flight.seats_booked, 1)
        self.assertEqual(flight.seats_left, 3)
        self.assertEqual(flight.fill_percent, 25)

    def test_seat_stats_by_class(self):
        flight = with_seat_stats(Flight.objects.all(), Seat.SeatClass.BUSINESS).get(pk=self.flight.pk)

        self.assertEqual(flight.seats_total, 1)
        self.assertEqual(flight.seats_left, 1)

    def test_home_without_search_shows_filling_up(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["searched"])
        self.assertIn(self.flight, response.context["filling_up"])
        self.assertEqual(response.context["booked_this_week"], 1)

    def test_search_finds_flight_on_date(self):
        date = self.flight.departure_time.date().isoformat()
        response = self.client.get(reverse("home"), {"from": "GDN", "to": "WAW", "date": date})

        self.assertEqual(list(response.context["results"]), [self.flight])
        self.assertContains(response, f'{reverse("booking-create")}?flight={self.flight.pk}')

    def test_search_wrong_date_gives_empty_results(self):
        response = self.client.get(reverse("home"), {"from": "GDN", "date": "2000-01-01"})

        self.assertEqual(list(response.context["results"]), [])
        self.assertContains(response, "No flights with free seats")

    def test_booking_form_gets_flight_from_url(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("booking-create"), {"flight": self.flight.pk})

        self.assertEqual(response.context["form"].initial["flight"], str(self.flight.pk))
