"""
Fill the database with demo data: airports, airlines, airplanes (with seats),
flights for the next days and some bookings, so the site is not empty.

Usage:
    python manage.py seed_demo            # flights for the next 14 days
    python manage.py seed_demo --days 30
    python manage.py seed_demo --no-bookings

Safe to run more than once: existing records are reused (get_or_create /
update_or_create), so a second run does not create duplicates.
"""
import random
import uuid
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from airlines.models import Airline
from airplanes.models import Airplane
from airplanes.views.airplanes import sync_airplane_seats
from airports.models import Airport
from bookings.models import Booking
from flights.models import Flight
from users.models import User

DEMO_USER_EMAIL = "demo@vezline.dev"
DEMO_USER_PASSWORD = "vezline-demo"
FILLER_USER_EMAIL = "passengers@vezline.dev"

AIRPORTS = [
    # code, name, city, country
    ("GDN", "Gdańsk Lech Wałęsa Airport", "Gdańsk", "Poland"),
    ("WAW", "Warsaw Chopin Airport", "Warsaw", "Poland"),
    ("KRK", "Kraków John Paul II Airport", "Kraków", "Poland"),
    ("WRO", "Wrocław Copernicus Airport", "Wrocław", "Poland"),
    ("LHR", "London Heathrow Airport", "London", "United Kingdom"),
    ("BCN", "Barcelona–El Prat Airport", "Barcelona", "Spain"),
    ("OSL", "Oslo Gardermoen Airport", "Oslo", "Norway"),
    ("FCO", "Rome Fiumicino Airport", "Rome", "Italy"),
    ("CDG", "Paris Charles de Gaulle Airport", "Paris", "France"),
    ("AMS", "Amsterdam Schiphol Airport", "Amsterdam", "Netherlands"),
]

# Fictional airlines, so the demo never pretends to be a real carrier.
AIRLINES = [
    # code, name, country, airplanes: (model, registration, economy, business, first)
    ("VZ", "Vezline Air", "Poland", [
        ("Airbus A320neo", "SP-VZA", 168, 12, 0),
        ("Airbus A321neo", "SP-VZB", 196, 16, 8),
    ]),
    ("BW", "Baltic Wings", "Poland", [
        ("Boeing 737-800", "SP-BWA", 174, 12, 0),
        ("Embraer E195", "SP-BWB", 112, 8, 0),
    ]),
    ("NS", "Nordic Sky", "Norway", [
        ("Boeing 737 MAX 8", "LN-NSA", 168, 12, 0),
        ("Airbus A220-300", "LN-NSB", 130, 10, 0),
    ]),
]

ROUTES = [
    # airline, from, to, departure hour, duration (min), base price
    ("VZ", "GDN", "WAW", 7, 60, "189.00"),
    ("VZ", "GDN", "LHR", 10, 125, "459.00"),
    ("VZ", "WAW", "CDG", 9, 150, "529.00"),
    ("VZ", "WAW", "FCO", 13, 155, "499.00"),
    ("BW", "GDN", "BCN", 12, 210, "599.00"),
    ("BW", "KRK", "AMS", 8, 120, "389.00"),
    ("BW", "WRO", "LHR", 15, 140, "419.00"),
    ("BW", "KRK", "WAW", 18, 55, "159.00"),
    ("NS", "GDN", "OSL", 14, 95, "349.00"),
    ("NS", "OSL", "AMS", 9, 120, "429.00"),
]


class Command(BaseCommand):
    help = "Fill the database with demo airports, airlines, airplanes, flights and bookings."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=14, help="How many days ahead to create flights for (default: 14).")
        parser.add_argument("--no-bookings", action="store_true", help="Do not create demo bookings.")

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(42)

        airports = self.create_airports()
        airlines, planes_by_airline = self.create_airlines_and_airplanes()
        demo_user, filler_user = self.create_users()

        new_flights = self.create_flights(options["days"], airports, airlines, planes_by_airline, rng)

        bookings_count = 0
        if not options["no_bookings"]:
            bookings_count = self.create_bookings(new_flights, filler_user, rng)

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {Airport.objects.count()} airports, {Airline.objects.count()} airlines, "
            f"{Airplane.objects.count()} airplanes, {len(new_flights)} new flights, {bookings_count} new bookings."
        ))
        self.stdout.write(f"Demo login: {DEMO_USER_EMAIL} / {DEMO_USER_PASSWORD}")

    def create_airports(self):
        airports = {}
        for code, name, city, country in AIRPORTS:
            airport, _ = Airport.objects.get_or_create(
                code=code,
                defaults={"name": name, "city": city, "country": country},
            )
            airports[code] = airport
        return airports

    def create_airlines_and_airplanes(self):
        airlines = {}
        planes_by_airline = {}
        for code, name, country, planes in AIRLINES:
            airline, _ = Airline.objects.get_or_create(
                code=code,
                defaults={"name": name, "country": country},
            )
            airlines[code] = airline
            planes_by_airline[code] = []

            for model, registration, economy, business, first in planes:
                airplane, created = Airplane.objects.get_or_create(
                    registration_number=registration,
                    defaults={
                        "airline": airline,
                        "model": model,
                        "capacity": economy + business + first,
                    },
                )
                if created:
                    # Same seat generation as the "Create airplane" page (1A, 1B, ...).
                    sync_airplane_seats(airplane, economy, business, first)
                planes_by_airline[code].append(airplane)
        return airlines, planes_by_airline

    def create_users(self):
        demo_user, created = User.objects.get_or_create(email=DEMO_USER_EMAIL)
        if created:
            demo_user.set_password(DEMO_USER_PASSWORD)
            demo_user.save()

        # Owns the "other passengers'" bookings, so seat maps are not empty.
        filler_user, created = User.objects.get_or_create(
            email=FILLER_USER_EMAIL,
            defaults={"is_active": False},
        )
        if created:
            filler_user.set_unusable_password()
            filler_user.save()
        return demo_user, filler_user

    def create_flights(self, days, airports, airlines, planes_by_airline, rng):
        tz = timezone.get_current_timezone()
        tomorrow = timezone.localdate() + timedelta(days=1)
        new_flights = []

        for route_index, (airline_code, origin, destination, hour, duration, base_price) in enumerate(ROUTES):
            planes = planes_by_airline[airline_code]

            for day_offset in range(days):
                day = tomorrow + timedelta(days=day_offset)
                departure = timezone.make_aware(datetime.combine(day, time(hour=hour)), tz)
                arrival = departure + timedelta(minutes=duration)

                # Outbound and return flight; the return leaves 1 hour after landing.
                legs = [
                    (origin, destination, departure, arrival, route_index * 2 + 1),
                    (destination, origin, arrival + timedelta(hours=1),
                     arrival + timedelta(hours=1, minutes=duration), route_index * 2 + 2),
                ]
                for leg_from, leg_to, leg_departure, leg_arrival, leg_no in legs:
                    # flight_number is unique, so the date is part of it: VZ01 + MMDD -> "VZ011104"
                    flight_number = f"{airline_code}{leg_no:02d}{leg_departure:%m%d}"
                    price = (Decimal(base_price) * Decimal(rng.choice(["0.8", "0.9", "1.0", "1.1", "1.25"]))).quantize(Decimal("1.00"))

                    flight, created = Flight.objects.get_or_create(
                        flight_number=flight_number,
                        defaults={
                            "airplane": planes[(day_offset + leg_no) % len(planes)],
                            "departure_airport": airports[leg_from],
                            "arrival_airport": airports[leg_to],
                            "departure_time": leg_departure,
                            "arrival_time": leg_arrival,
                            "price": price,
                        },
                    )
                    if created:
                        new_flights.append(flight)
        return new_flights

    def create_bookings(self, flights, user, rng):
        bookings = []
        for flight in flights:
            seats = list(flight.airplane.seats.all())
            share = rng.uniform(0.1, 0.6)  # 10–60% of seats already taken
            for seat in rng.sample(seats, int(len(seats) * share)):
                bookings.append(Booking(
                    user=user,
                    flight=flight,
                    seat=seat,
                    booking_number=uuid.uuid4().hex[:8].upper(),
                    status=Booking.Status.CONFIRMED,
                ))
        Booking.objects.bulk_create(bookings, batch_size=1000)
        return len(bookings)
