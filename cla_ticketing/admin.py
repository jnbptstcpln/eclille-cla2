from django.contrib import admin
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings

from cla_ticketing.models import *


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    class EventRegistrationTypeInline(admin.TabularInline):
        fields = ['name', 'description', 'price']
        model = EventRegistrationType
        classes = ['collapse']

    class EventRegistrationInline(admin.TabularInline):
        fields = ['last_name', 'first_name', 'email', 'created_on', 'is_contributor']
        readonly_fields = ['last_name', 'first_name', 'email', 'created_on', 'is_contributor']
        model = EventRegistration
        classes = ['collapse']
        max_num = 0
        extra = 0

        can_delete = False
        template = "cla_ticketing/admin/change_event_registrations.html"

        def is_contributor(self, obj: EventRegistration):
            return obj.is_contributor
        is_contributor.short_description = "Cotisants ?"

    list_display = ("name", "event_starts_on", "organizer", "places")
    change_form_template = "cla_ticketing/admin/change_event.html"
    filter_horizontal = ('managers',)
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
                'fields': ('ticketing_href', 'allow_non_contributor_registration', 'colleges', 'description'),
                'classes': ('collapse',),
            }
        ],
        [
            "Administration de l'événement",
            {
                'fields': ('managers',),
                'classes': ('collapse',),
            }
        ]
    ]
    readonly_fields = ['link_ticketing']
    inlines = [EventRegistrationTypeInline, EventRegistrationInline]

    def link_ticketing(self, obj: Event):
        return mark_safe(
            (
                "<label style='float:none;width:100%'>Voici le lien pour accéder à la billeterie</label>"
                "<input style='margin-right: .5rem' class='vTextField' value='{link_ticketing}' id='id_link_ticketing'>"
                "<a class='button' onclick='document.getElementById(\"id_link_ticketing\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
            ).format(link_ticketing=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_ticketing:event_ticketing', obj.slug)}")
        )
    link_ticketing.short_description = ''



@admin.register(DancingParty)
class DancingPartyAdmin(admin.ModelAdmin):
    pass