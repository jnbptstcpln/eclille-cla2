
from django.contrib import admin

from cla_reservation.models import FoyerRules, ReservationFoyer, BeerMenu, FoyerItem
from cla_reservation.models.foyer import BlockedSlotFoyer


@admin.register(BeerMenu)
class BeerMenuAdmin(admin.ModelAdmin):
    pass


@admin.register(FoyerRules)
class FoyerRulesAdmin(admin.ModelAdmin):
    pass


@admin.register(FoyerItem)
class FoyerItemAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationFoyer)
class ReservationFoyerAdmin(admin.ModelAdmin):
    list_display = [
        'start_date',
        'start_time',
        'event',
        'user'
    ]


@admin.register(BlockedSlotFoyer)
class BlockedSlotFoyerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'start_date',
        'start_time',
        'end_time',
        'recurring'
    ]
