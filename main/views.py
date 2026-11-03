from datetime import timedelta

from django.db.models import Count, ExpressionWrapper, F, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce, NullIf
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView

from airports.models import Airport
from bookings.models import Booking
from flights.models import Flight
from seats.models import Seat

DEFAULT_ORIGIN_CODE = "GDN"
RESULTS_LIMIT = 20
FILLING_UP_LIMIT = 3

# English labels for the home page (Seat.SeatClass labels are in Ukrainian)
SEAT_CLASS_CHOICES = [
    ("", "Any class"),
    (Seat.SeatClass.ECONOMY, "Economy"),
    (Seat.SeatClass.BUSINESS, "Business"),
    (Seat.SeatClass.FIRST, "First"),
]


def with_seat_stats(flights, seat_class=""):
    """
    Add seats_total, seats_booked, seats_left and fill_percent to each flight.

    Counts are subqueries, not JOINs: two Count() over different relations
    (seats and bookings) in one query multiply rows and give wrong numbers.
    If seat_class is given, only seats of that class are counted.
    """
    seats = Seat.objects.filter(airplane=OuterRef("airplane"))
    booked = Booking.objects.filter(
        flight=OuterRef("pk"),
        status=Booking.Status.CONFIRMED,
    )
    if seat_class:
        seats = seats.filter(seat_class=seat_class)
        booked = booked.filter(seat__seat_class=seat_class)

    seats_count = seats.order_by().values("airplane").annotate(n=Count("pk")).values("n")
    booked_count = booked.order_by().values("flight").annotate(n=Count("pk")).values("n")

    return flights.annotate(
        seats_total=Coalesce(Subquery(seats_count, output_field=IntegerField()), 0),
        seats_booked=Coalesce(Subquery(booked_count, output_field=IntegerField()), 0),
    ).annotate(
        seats_left=F("seats_total") - F("seats_booked"),
        fill_percent=ExpressionWrapper(
            F("seats_booked") * 100 / NullIf(F("seats_total"), 0),
            output_field=IntegerField(),
        ),
    )


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        params = self.request.GET

        origin_code = params.get("from", DEFAULT_ORIGIN_CODE)
        destination_code = params.get("to", "")
        travel_date = parse_date(params.get("date", "") or "")
        seat_class = params.get("class", "")
        if seat_class not in Seat.SeatClass.values:
            seat_class = ""

        upcoming = Flight.objects.filter(
            status=Flight.Status.SCHEDULED,
            departure_time__gt=now,
        ).select_related(
            "airplane__airline",
            "departure_airport",
            "arrival_airport",
        )

        # The form was submitted when "from" is in the URL (?from=GDN&to=...)
        searched = "from" in params
        results = []
        if searched:
            results = upcoming.filter(departure_airport__code=origin_code)
            if destination_code:
                results = results.filter(arrival_airport__code=destination_code)
            if travel_date:
                results = results.filter(departure_time__date=travel_date)
            results = (
                with_seat_stats(results, seat_class)
                .filter(seats_left__gt=0)
                .order_by("departure_time")[:RESULTS_LIMIT]
            )

        filling_up = (
            with_seat_stats(upcoming.filter(departure_time__lt=now + timedelta(days=7)))
            .filter(seats_total__gt=0, seats_left__gt=0)
            .order_by("-fill_percent", "departure_time")[:FILLING_UP_LIMIT]
        )

        airports = Airport.objects.order_by("city")
        airports_by_code = {airport.code: airport for airport in airports}

        context.update({
            "airports": airports,
            "seat_classes": SEAT_CLASS_CHOICES,
            "selected": {
                "origin": origin_code,
                "destination": destination_code,
                "date": travel_date.isoformat() if travel_date else "",
                "seat_class": seat_class,
            },
            "origin": airports_by_code.get(origin_code),
            "destination": airports_by_code.get(destination_code),
            "travel_date": travel_date,
            "seat_class_label": dict(SEAT_CLASS_CHOICES).get(seat_class) if seat_class else "",
            "today": timezone.localdate().isoformat(),
            "searched": searched,
            "results": results,
            "filling_up": filling_up,
            "booked_this_week": Booking.objects.filter(
                status=Booking.Status.CONFIRMED,
                created_at__gte=now - timedelta(days=7),
            ).count(),
        })
        return context
