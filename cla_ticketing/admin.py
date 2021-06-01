from django.contrib import admin
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe
from django.conf import settings

from cla_ticketing.models import *


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    class EventRegistrationTypeInline(admin.TabularInline):
        fields = ['name', 'description', 'price']
        model = EventRegistrationType

    change_form_template = "cla_ticketing/admin/change_event.html"
    fieldsets = [
        [
            "Informations pratiques",
            {
                'fields': (
                    ('link_ticketing'),
                    ('name', 'slug'),
                    ('organizer', 'places'),
                    ('event_starts_on', 'event_ends_on'),
                    ('registration_starts_on', 'registration_ends_on')
                )
            }
        ],
        [
            "Informations supplémentaire",
            {
                'fields': ('ticketing_href', 'colleges', 'description'),
                'classes': ('collapse',),
            }
        ]
    ]
    readonly_fields = ['link_ticketing']

    def link_ticketing(self, obj: Event):
        return mark_safe(
            (
                "<label style='float:none;width:100%'>Voici le lien pour accéder à la billeterie</label>"
                "<input style='margin-right: .5rem' class='vTextField' value='{link_ticketing}' id='id_link_ticketing'>"
                "<a class='button' onclick='document.getElementById(\"id_link_ticketing\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
            ).format(link_ticketing=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_ticketing:event_ticketing', obj.slug)}")
        )
    link_ticketing.short_description = ''

    inlines = [EventRegistrationTypeInline]


@admin.register(DancingParty)
class DancingPartyAdmin(admin.ModelAdmin):
    pass