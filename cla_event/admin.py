
from django.contrib import admin

from cla_event.models import EventType, EventPlace, Event


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(EventPlace)
class EventPlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'start_date',
        'start_time',
        'association',
        'name',
        'type',
        'place'
    ]
