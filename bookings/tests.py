from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from airlines.models import Airline
from airplanes.models import Airplane
from airports.models import Airport
from bookings.models import Booking
from bookings.seat_map import group_seats
from flights.models import Flight
from payments.models import Payment
from seats.models import Seat
from users.models import User


class SeatMapGroupingTests(TestCase):
    def test_seats_are_grouped_by_row_with_aisle_sides(self):
        plane = Airplane(id=1, registration_number="SP-X", capacity=4)
        seats = [
            Seat(id=1, airplane=plane, number="1A"),
            Seat(id=2, airplane=plane, number="1F"),
            Seat(id=3, airplane=plane, number="2C", seat_class=Seat.SeatClass.BUSINESS),
            Seat(id=4, airplane=plane, number="7"),  # old digit-only seat
        ]

        seat_map = group_seats(seats, taken_ids={2}, selected_seat_id="3")

        first_row, second_row = seat_map["rows"]
        self.assertEqual(first_row["number"], 1)
        self.assertEqual(first_row["left"][0]["number"], "1A")
        self.assertIsNone(first_row["left"][1])  # 1B does not exist
        self.assertTrue(first_row["right"][2]["taken"])  # 1F is booked
        self.assertEqual(second_row["class_start"], Seat.SeatClass.BUSINESS)
        self.assertEqual(seat_map["selected"]["number"], "2C")
        self.assertEqual([cell["number"] for cell in seat_map["other"]], ["7"])
        self.assertEqual((seat_map["free"], seat_map["total"]), (3, 4))


class BookingFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        gdn = Airport.objects.create(name="Lech Wałęsa", code="GDN", city="Gdańsk", country="Poland")
        osl = Airport.objects.create(name="Gardermoen", code="OSL", city="Oslo", country="Norway")
        airline = Airline.objects.create(name="Nordic Sky", code="NS", country="Norway")
        plane = Airplane.objects.create(airline=airline, model="A220", registration_number="LN-TST", capacity=3)
        cls.seat_1a = Seat.objects.create(airplane=plane, number="1A")
        cls.seat_1b = Seat.objects.create(airplane=plane, number="1B")
        cls.seat_1c = Seat.objects.create(airplane=plane, number="1C")
        departure = timezone.now() + timedelta(days=3)
        cls.flight = Flight.objects.create(
            airplane=plane,
            departure_airport=gdn,
            arrival_airport=osl,
            flight_number="NS100",
            departure_time=departure,
            arrival_time=departure + timedelta(hours=2),
            price="349.00",
        )
        cls.user = User.objects.create_user(email="flyer@vezline.dev", password="test-pass-123")
        other = User.objects.create_user(email="other@vezline.dev", password="test-pass-123")
        Booking.objects.create(user=other, flight=cls.flight, seat=cls.seat_1a, booking_number="TAKEN1")

    def setUp(self):
        self.client.force_login(self.user)

    def test_seat_map_shows_taken_seat_as_disabled(self):
        response = self.client.get(reverse("booking-create"), {"flight": self.flight.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.seat_1a.pk}" data-label="1A · Economy" disabled')
        self.assertEqual(response.context["seat_map"]["free"], 2)

    def test_booking_a_seat_goes_to_payment(self):
        response = self.client.post(
            reverse("booking-create"),
            {"flight": self.flight.pk, "seat": self.seat_1b.pk},
        )

        booking = Booking.objects.get(user=self.user)
        self.assertRedirects(response, f"{reverse('payment-create')}?booking={booking.pk}")
        self.assertEqual(booking.seat, self.seat_1b)

    def test_taken_seat_cannot_be_booked(self):
        response = self.client.post(
            reverse("booking-create"),
            {"flight": self.flight.pk, "seat": self.seat_1a.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(user=self.user).exists())
        self.assertTrue(response.context["form"].errors["seat"])

    def test_seat_is_required(self):
        response = self.client.post(reverse("booking-create"), {"flight": self.flight.pk})

        self.assertContains(response, "Pick a seat on the map.")

    def test_change_seat_keeps_own_seat_free(self):
        booking = Booking.objects.create(
            user=self.user, flight=self.flight, seat=self.seat_1b, booking_number="MINE01",
        )
        response = self.client.get(reverse("booking-edit", args=[booking.pk]))

        own_seat = response.context["seat_map"]["selected"]
        self.assertEqual(own_seat["number"], "1B")
        self.assertFalse(own_seat["taken"])

    def test_my_bookings_shows_pay_button_until_paid(self):
        booking = Booking.objects.create(
            user=self.user, flight=self.flight, seat=self.seat_1c, booking_number="MINE02",
        )
        pay_url = f"{reverse('payment-create')}?booking={booking.pk}"

        self.assertContains(self.client.get(reverse("booking-list")), pay_url)

        Payment.objects.create(booking=booking, payment_method=Payment.PaymentMethod.BLIK)
        self.assertNotContains(self.client.get(reverse("booking-list")), pay_url)

    def test_payment_page_shows_chosen_booking(self):
        booking = Booking.objects.create(
            user=self.user, flight=self.flight, seat=self.seat_1c, booking_number="MINE03",
        )
        response = self.client.get(reverse("payment-create"), {"booking": booking.pk})

        self.assertEqual(response.context["booking"], booking)
        self.assertContains(response, "Pay 349 PLN")
