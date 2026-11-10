from seats.models import Seat
from django.contrib import admin

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("number", "airplane", "seat_class")
    list_filter = ("airplane", "seat_class")
    search_fields = ("number", "airplane__model")
    list_editable = ("seat_class",)
    list_per_page = 50