
from django.contrib import admin

from cla_reservation.models import BibliRules, ReservationBibli, BlockedSlotBibli


@admin.register(BibliRules)
class BibliRuleAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationBibli)
class ReservationBibliAdmin(admin.ModelAdmin):
    list_display = [
        'start_date',
        'start_time',
        'event',
        'user'
    ]


@admin.register(BlockedSlotBibli)
class BlockedSlotBibliAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'start_date',
        'start_time',
        'end_time',
        'recurring'
    ]
