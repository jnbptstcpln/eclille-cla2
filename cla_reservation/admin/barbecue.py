
from django.contrib import admin

from cla_event.models import EventType, EventPlace, Event
from cla_reservation.models import BarbecueRules, ReservationBarbecue
from cla_reservation.models.barbecue import BlockedSlotBarbecue


@admin.register(BarbecueRules)
class BarbecueRuleAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationBarbecue)
class ReservationBarbecueAdmin(admin.ModelAdmin):
    list_display = [
        'start_date',
        'start_time',
        'event',
        'user'
    ]


@admin.register(BlockedSlotBarbecue)
class BlockedSlotBarbecueAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'start_date',
        'start_time',
        'end_time',
        'recurring'
    ]
