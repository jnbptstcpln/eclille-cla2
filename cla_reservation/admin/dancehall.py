
from django.contrib import admin

from cla_reservation.models import ReservationDanceHall, BlockedSlotDanceHall


@admin.register(ReservationDanceHall)
class ReservationDanceHallAdmin(admin.ModelAdmin):
    list_display = [
        'start_date',
        'start_time',
        'event',
        'user'
    ]


@admin.register(BlockedSlotDanceHall)
class BlockedSlotDanceHallAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'start_date',
        'start_time',
        'end_time',
        'recurring'
    ]
