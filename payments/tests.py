from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from airlines.models import Airline
from airplanes.models import Airplane
from airports.models import Airport
from bookings.models import Booking
from flights.models import Flight
from payments.models import Payment
from seats.models import Seat
from users.models import User


class PaymentViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        gdn = Airport.objects.create(name="Lech Wałęsa", code="GDN", city="Gdańsk", country="Poland")
        bcn = Airport.objects.create(name="El Prat", code="BCN", city="Barcelona", country="Spain")
        airline = Airline.objects.create(name="Baltic Wings", code="BW", country="Poland")
        plane = Airplane.objects.create(airline=airline, model="E195", registration_number="SP-PAY", capacity=2)
        seat_a = Seat.objects.create(airplane=plane, number="1A")
        seat_b = Seat.objects.create(airplane=plane, number="1B")
        departure = timezone.now() + timedelta(days=5)
        flight = Flight.objects.create(
            airplane=plane,
            departure_airport=gdn,
            arrival_airport=bcn,
            flight_number="BW200",
            departure_time=departure,
            arrival_time=departure + timedelta(hours=3),
            price="599.00",
        )
        cls.user = User.objects.create_user(email="payer@vezline.dev", password="test-pass-123")
        cls.other = User.objects.create_user(email="stranger@vezline.dev", password="test-pass-123")
        cls.booking = Booking.objects.create(user=cls.user, flight=flight, seat=seat_a, booking_number="PAY001")
        other_booking = Booking.objects.create(user=cls.other, flight=flight, seat=seat_b, booking_number="PAY002")
        cls.other_payment = Payment.objects.create(booking=other_booking, payment_method=Payment.PaymentMethod.CARD)

    def setUp(self):
        self.client.force_login(self.user)

    def test_list_needs_login(self):
        self.client.logout()
        response = self.client.get(reverse("payment-list"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('payment-list')}")

    def test_list_shows_only_own_payments(self):
        own = Payment.objects.create(booking=self.booking, payment_method=Payment.PaymentMethod.BLIK)
        response = self.client.get(reverse("payment-list"))

        self.assertEqual(list(response.context["payments"]), [own])

    def test_create_payment_takes_price_from_flight(self):
        response = self.client.post(
            reverse("payment-create"),
            {"booking": self.booking.pk, "payment_method": Payment.PaymentMethod.BLIK},
        )

        payment = Payment.objects.get(booking=self.booking)
        self.assertRedirects(response, reverse("payment-list"))
        self.assertEqual(payment.amount, Decimal("599.00"))

    def test_create_page_preselects_booking_from_url(self):
        response = self.client.get(reverse("payment-create"), {"booking": self.booking.pk})

        self.assertEqual(response.context["booking"], self.booking)
        self.assertContains(response, f'name="booking" value="{self.booking.pk}"')

    def test_cannot_pay_for_someone_elses_booking(self):
        foreign_booking = self.other_payment.booking
        self.other_payment.delete()

        response = self.client.post(
            reverse("payment-create"),
            {"booking": foreign_booking.pk, "payment_method": Payment.PaymentMethod.CARD},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("booking", response.context["form"].errors)
        self.assertFalse(Payment.objects.filter(booking=foreign_booking).exists())

    def test_someone_elses_payment_is_404(self):
        for name in ("payment-edit", "payment-delete"):
            response = self.client.get(reverse(name, args=[self.other_payment.pk]))
            self.assertEqual(response.status_code, 404)

    def test_edit_changes_method(self):
        payment = Payment.objects.create(booking=self.booking, payment_method=Payment.PaymentMethod.CARD)
        self.client.post(reverse("payment-edit", args=[payment.pk]), {"payment_method": Payment.PaymentMethod.PAYPAL})

        payment.refresh_from_db()
        self.assertEqual(payment.payment_method, Payment.PaymentMethod.PAYPAL)

    def test_delete_removes_payment(self):
        payment = Payment.objects.create(booking=self.booking, payment_method=Payment.PaymentMethod.CARD)
        response = self.client.post(reverse("payment-delete", args=[payment.pk]))

        self.assertRedirects(response, reverse("payment-list"))
        self.assertFalse(Payment.objects.filter(pk=payment.pk).exists())
