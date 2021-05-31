from django.contrib import admin
from cla_ticketing.models import *


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(DancingParty)
class DancingPartyAdmin(admin.ModelAdmin):
    pass