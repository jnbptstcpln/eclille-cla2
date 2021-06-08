from copy import deepcopy

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import resolve_url, get_object_or_404
from django.utils.safestring import mark_safe
from django.conf import settings

from cla_ticketing.models import *
from cla_ticketing.forms import AdminEventRegistrationForm


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    class EventRegistrationTypeInline(admin.TabularInline):
        fields = ['name', 'description', 'open_to', 'visible', 'price']
        model = EventRegistrationType
        classes = []
        extra = 0

        def has_add_permission(self, request, obj: Event = None):
            perm = super().has_add_permission(request, obj)
            if request.user.has_perm('cla_ticketing.event_manager'):
                perm = True
            return perm

        def has_view_permission(self, request: HttpRequest, obj: Event = None):
            perm = super().has_view_permission(request, obj)
            if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
                if obj:
                    perm = obj.managers.filter(pk=request.user.pk).count() > 0
                else:
                    perm = True
            return perm

        def has_change_permission(self, request: HttpRequest, obj: Event = None):
            perm = super().has_change_permission(request, obj)
            if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
                if obj:
                    perm = obj.managers.filter(pk=request.user.pk).count() > 0
                else:
                    perm = True
            return perm

        def has_delete_permission(self, request: HttpRequest, obj: Event = None):
            perm = super().has_delete_permission(request, obj)
            if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
                if obj:
                    perm = obj.managers.filter(pk=request.user.pk).count() > 0
                else:
                    perm = True
            return perm

    class EventRegistrationInline(admin.TabularInline):
        fields = ['last_name', 'first_name', 'created_on', 'is_contributor', 'type', 'paid', 'edit_button']
        readonly_fields = ['last_name', 'first_name', 'created_on', 'is_contributor', 'type', 'paid', 'edit_button']
        model = EventRegistration
        classes = []
        max_num = 0

        can_delete = False
        template = "cla_ticketing/admin/change_event_registrations.html"

        def is_contributor(self, obj: EventRegistration):
            return obj.is_contributor

        is_contributor.short_description = "Cotisant ?"
        is_contributor.boolean = True

        def edit_button(self, obj: EventRegistration):
            return mark_safe(
                f"<a id='change_id_registrations-{obj.id}-eventregistration' class='related-widget-wrapper-link change-related' data-href-template='/admin/cla_ticketing/eventregistration/__fk__/change/?_to_field=id&amp;_popup=1' title='Modifier l\\'inscription' href='/admin/cla_ticketing/eventregistration/{obj.id}/change/?_to_field=id&amp;_popup=1&amp;event={obj.event.pk}' onclick='django.jQuery(this).parents(\"tr\").children().css(\"background-color\", \"rgb(255,255,205,.25)\")'><img src='/static/admin/img/icon-changelink.svg' alt='Modification'></a>" +
                f"<a id='change_id_registrations-{obj.id}-eventregistration' class='related-widget-wrapper-link delete-related' data-href-template='/admin/cla_ticketing/eventregistration/__fk__/delete/?_to_field=id&amp;_popup=1' title='Supprimer l\\'inscription' href='/admin/cla_ticketing/eventregistration/{obj.id}/delete/?_to_field=id&amp;_popup=1' onclick='django.jQuery(this).parents(\"tr\").children().css(\"background-color\", \"rgb(255,0,0,.25)\")'><img src='/static/admin/img/icon-deletelink.svg' alt='Supprimer'></a>"
            )

        edit_button.short_description = mark_safe(
            "edit_button"
        )

        def get_model_perms(self, request):
            perms = super().get_model_perms(request)
            return perms

        def has_view_permission(self, request: HttpRequest, obj: Event = None):
            perm = super().has_view_permission(request, obj)
            if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
                if obj:
                    perm = obj.managers.filter(pk=request.user.pk).count() > 0
                else:
                    perm = True
            return perm



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
                'fields': ('contributor_ticketing_href', 'non_contributor_ticketing_href', 'allow_non_contributor_registration', 'colleges', 'description'),
                'classes': ('collapse',),
            }
        ]
    ]
    fielset_event_administration = [
        "Administration de l'événement",
        {
            'fields': ('managers',),
            'classes': ('collapse',),
        }
    ]
    readonly_fields = ['link_ticketing']

    create_inlines = [EventRegistrationTypeInline]
    change_inlines = [EventRegistrationTypeInline, EventRegistrationInline]

    def link_ticketing(self, obj: Event):
        if obj.pk:  # Check if the object was created
            return mark_safe(
                (
                    "<label style='float:none;width:100%'>Voici le lien pour accéder à la billeterie</label>"
                    "<input style='margin-right: .5rem' class='vTextField' value='{link_ticketing}' id='id_link_ticketing'>"
                    "<a class='button' onclick='document.getElementById(\"id_link_ticketing\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
                ).format(link_ticketing=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_ticketing:event_ticketing', obj.slug)}")
            )
        else:
            return ""

    link_ticketing.short_description = ''

    def response_add(self, request, obj, post_url_continue=None):
        self.update_managers(request, obj)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        self.update_managers(request, obj)
        return super().response_change(request, obj)

    def update_managers(self, request, obj: Event):
        # Update manager perms to allow them to access the event
        if request.user.has_perm('cla_ticketing.add_event'):
            event_organizer_group = Event.get_or_create_event_organizer_group()
            for manager in obj.managers.all():
                manager.is_staff = True
                manager.save()
                event_organizer_group.user_set.add(manager)
                event_organizer_group.save()

        return super()._response_post_save(request, obj)

    def get_fieldsets(self, request: HttpRequest, obj=None):
        fielsets = deepcopy(super().get_fieldsets(request, obj))
        if request.user.has_perm("cla_ticketing.add_event"):
            fielsets.append(self.fielset_event_administration)
        return fielsets

    def get_inlines(self, request, obj=None):
        if obj:
            return self.change_inlines
        else:
            return self.create_inlines

    def has_view_permission(self, request, obj=None):
        perm = super().has_view_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = True
        return perm

    def has_change_permission(self, request: HttpRequest, obj: Event = None):
        perm = super().has_change_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.managers.filter(pk=request.user.pk).count() > 0
        return perm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            qs = qs.filter(managers__in=[request.user])
        return qs


@admin.register(EventRegistrationType)
class EventRegistrationTypeAdmin(admin.ModelAdmin):

    def get_model_perms(self, request):
        return {}

    def has_add_permission(self, request):
        perm = super().has_add_permission(request)
        if request.user.has_perm('cla_ticketing.event_manager'):
            perm = True
        return perm

    def has_view_permission(self, request: HttpRequest, obj: EventRegistrationType = None):
        perm = super().has_view_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.event.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = False
        return perm

    def has_change_permission(self, request: HttpRequest, obj: EventRegistrationType = None):
        perm = super().has_change_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.event.managers.filter(pk=request.user.pk).count() > 0
        return perm

    def has_delete_permission(self, request: HttpRequest, obj: EventRegistrationType = None):
        perm = super().has_delete_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.event.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = False
        return perm


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    form = AdminEventRegistrationForm
    event = None

    def get_event_from_request(self, request):
        event = get_object_or_404(Event, pk=request.GET.get('event', None))
        if event.managers.filter(pk=request.user.pk).count() == 0:
            raise PermissionDenied()
        return event

    def save_model(self, request, obj: EventRegistration, form, change):
        if not change:
            obj.created_by = request.user
        obj.student_status = EventRegistration.StudentStatus.CONTRIBUTOR if obj.user else EventRegistration.StudentStatus.NON_CONTRIBUTOR
        obj.event = self.get_event_from_request(request)
        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Update queryset to only show RegistrationType related to the event
        if db_field.name == "type":
            return forms.ModelChoiceField(
                EventRegistrationType.objects.filter(
                    event=self.get_event_from_request(request)
                )
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return {}

    def has_add_permission(self, request):
        perm = super().has_add_permission(request)
        if request.user.has_perm('cla_ticketing.event_manager'):
            perm = True
        return perm

    def has_view_permission(self, request: HttpRequest, obj: EventRegistration = None):
        perm = super().has_view_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.event.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = False
        return perm

    def has_change_permission(self, request: HttpRequest, obj: EventRegistration = None):
        perm = super().has_change_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.event.managers.filter(pk=request.user.pk).count() > 0
        return perm

    def has_delete_permission(self, request: HttpRequest, obj: EventRegistration = None):
        perm = super().has_delete_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_event') and request.user.has_perm('cla_ticketing.event_manager'):
            if obj:
                perm = obj.event.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = False
        return perm


@admin.register(DancingParty)
class DancingPartyAdmin(admin.ModelAdmin):
    pass
