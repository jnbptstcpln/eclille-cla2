
from django.contrib import admin

from cla_reservation.models import FoyerRules, ReservationFoyer, BeerMenu, FoyerItem, SportActivity, ReservationSynthe


@admin.register(SportActivity)
class SportActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationSynthe)
class ReservationSyntheAdmin(admin.ModelAdmin):
    list_display = [
        'start_date',
        'start_time',
        'event',
        'user'
    ]
