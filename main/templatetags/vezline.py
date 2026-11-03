from django import template

register = template.Library()

# Badge colour for every status value used in the project
STATUS_BADGES = {
    "CONFIRMED": "ok",
    "PAID": "ok",
    "SCHEDULED": "ok",
    "COMPLETED": "",
    "PENDING": "pending",
    "CANCELLED": "danger",
    "FAILED": "danger",
}


@register.filter
def choice_label(value):
    """
    English label from a choice value: "BANK_TRANSFER" -> "Bank transfer".

    Some model choices have Ukrainian labels (Seat, Booking, Flight),
    while the site is in English, so templates show the value instead.
    """
    return str(value or "").replace("_", " ").capitalize()


@register.filter
def status_badge(value):
    """CSS modifier for .vz-badge: {{ booking.status|status_badge }} -> "ok"."""
    return STATUS_BADGES.get(str(value), "")
