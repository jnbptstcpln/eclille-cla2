from copy import deepcopy

from django import forms
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, Http404
from django.shortcuts import resolve_url, get_object_or_404
from django.utils.safestring import mark_safe
from django.conf import settings

from cla_ticketing.models import *
from cla_ticketing.forms import AdminEventRegistrationForm
from cla_ticketing.views.admin import EventRegistrationExportView, DancingPartyRegistrationTooglePaidView


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    class EventRegistrationTypeInline(admin.TabularInline):
        fields = ['name', 'description', 'open_to', 'visible', 'price']
        model = EventRegistrationType
        classes = ["collapse"]
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

    class EventRegistrationInline(TabularInlinePaginated):
        fields = ['last_name', 'first_name', 'created_on', 'is_contributor', 'type', 'paid', 'edit_button']
        readonly_fields = ['last_name', 'first_name', 'created_on', 'is_contributor', 'type', 'paid', 'edit_button']
        model = EventRegistration
        classes = []
        per_page = 10
        max_num = 0
        ordering = "-created_on",

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

        def get_queryset(self, request):
            queryset = super().get_queryset(request)
            if request.GET.get('registration_search') is not None:
                queryset = queryset.filter(Q(last_name__icontains=request.GET.get('registration_search')) | Q(first_name__icontains=request.GET.get('registration_search')))
            return queryset

    list_display = ("name", "event_starts_on", "organizer", "places")
    change_form_template = "cla_ticketing/admin/change_event.html"
    filter_horizontal = ('managers',)
    fieldsets = [
        [
            "Informations pratiques",
            {
                'fields': (
                    ('link_ticketing'),
                    ('remaining_places'),
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
    readonly_fields = ['link_ticketing', 'remaining_places']

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

    def remaining_places(self, obj: Event):
        if obj.pk:  # Check if the object was created
            return obj.places_remaining
        else:
            return "L'événement n'a pas encore été créé"
    remaining_places.short_description = 'Nombre de places restant'

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

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        my_urls = [
            path(
                '<int:event_pk>/registrations/export',
                self.admin_site.admin_view(EventRegistrationExportView.as_view()),
                name='%s_%s_export' % info
            )
        ]
        urls = my_urls + urls
        return urls


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
        if not request.user.has_perm('cla_ticketing.add_event') and event.managers.filter(pk=request.user.pk).count() == 0:
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

    class DancingPartyRegistrationInline(TabularInlinePaginated):
        fields = ['last_name', 'first_name', 'place', 'place_paid', 'created_on', 'edit_button']
        readonly_fields = ['last_name', 'first_name', 'place', 'place_paid', 'created_on', 'edit_button']
        model = DancingPartyRegistration
        classes = []
        per_page = 10
        max_num = 0
        ordering = "-created_on",

        can_delete = False
        template = "cla_ticketing/admin/partyregistrations_inline.html"

        def edit_button(self, obj: DancingPartyRegistration):
            return mark_safe(
                f"<a title='Modifier l\\'inscription' href='/admin/cla_ticketing/dancingpartyregistration/{obj.id}/change/?_to_field=id&amp;dancingparty={obj.dancing_party.pk}' style='margin-right: 3px'><img src='/static/admin/img/icon-changelink.svg' alt='Modification'></a>"
            )
        edit_button.short_description = mark_safe(
            "edit_button"
        )

        def place(self, obj: DancingPartyRegistration):
            if obj.is_staff:
                return f"Staff : {obj.staff_description}"
            elif obj.student_status == DancingPartyRegistration.StudentStatus.CONTRIBUTOR:
                return f"Cotisant {obj.get_type_display().lower()}"
            elif obj.student_status == DancingPartyRegistration.StudentStatus.CONTRIBUTOR:
                return f"Non cotisant {obj.get_type_display().lower()}"
            else:
                return "Autre"
        place.short_description = "Place"

        def place_paid(self, obj: DancingPartyRegistration):
            icon = '<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.paid else '<img src="/static/admin/img/icon-no.svg" alt="False">'
            return mark_safe(
                f"<a class='place-paid' href='{resolve_url('admin:cla_ticketing_dancingparty_toggle_paid', obj.dancing_party.pk, obj.pk)}'>{icon}</a>"
            )
        place_paid.short_description = "Réglée ?"

        def get_model_perms(self, request):
            perms = super().get_model_perms(request)
            return perms

        def has_view_permission(self, request: HttpRequest, obj: Event = None):
            perm = super().has_view_permission(request, obj)
            if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.event_manager'):
                if obj:
                    perm = obj.managers.filter(pk=request.user.pk).count() > 0
                else:
                    perm = True
            return perm

        def get_queryset(self, request):
            queryset = super().get_queryset(request)
            if request.GET.get('registration_search') is not None:
                queryset = queryset.filter(Q(last_name__icontains=request.GET.get('registration_search')) | Q(first_name__icontains=request.GET.get('registration_search')))
            return queryset

    list_display = ("name", "event_starts_on", "organizer", "places")
    change_form_template = "cla_ticketing/admin/change_party.html"
    filter_horizontal = ('managers',)
    fieldsets = [
        [
            "Informations pratiques",
            {
                'fields': (
                    ('link_ticketing'),
                    ('remaining_places'),
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
                'fields': ('contributor_ticketing_href', 'colleges', 'description'),
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
    readonly_fields = ['link_ticketing', 'remaining_places']

    create_inlines = []
    change_inlines = [DancingPartyRegistrationInline]

    def link_ticketing(self, obj: Event):
        if obj.pk:  # Check if the object was created
            return mark_safe(
                (
                    "<label style='float:none;width:100%'>Voici le lien pour accéder à la billeterie</label>"
                    "<input style='margin-right: .5rem' class='vTextField' value='{link_ticketing}' id='id_link_ticketing'>"
                    "<a class='button' onclick='document.getElementById(\"id_link_ticketing\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
                ).format(link_ticketing=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_ticketing:party_ticketing', obj.slug)}")
            )
        else:
            return ""

    link_ticketing.short_description = ''

    def remaining_places(self, obj: Event):
        if obj.pk:  # Check if the object was created
            return obj.places_remaining
        else:
            return "L'événement n'a pas encore été créé"

    remaining_places.short_description = 'Nombre de places restant'

    def response_add(self, request, obj, post_url_continue=None):
        self.update_managers(request, obj)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        self.update_managers(request, obj)
        return super().response_change(request, obj)

    def update_managers(self, request, obj: Event):
        # Update manager perms to allow them to access the event
        if request.user.has_perm('cla_ticketing.add_dancingparty'):
            event_organizer_group = Event.get_or_create_event_organizer_group()
            for manager in obj.managers.all():
                manager.is_staff = True
                manager.save()
                event_organizer_group.user_set.add(manager)
                event_organizer_group.save()

        return super()._response_post_save(request, obj)

    def get_fieldsets(self, request: HttpRequest, obj=None):
        fielsets = deepcopy(super().get_fieldsets(request, obj))
        if request.user.has_perm("cla_ticketing.add_dancingparty"):
            fielsets.append(self.fielset_event_administration)
        return fielsets

    def get_inlines(self, request, obj=None):
        if obj:
            return self.change_inlines
        else:
            return self.create_inlines

    def has_view_permission(self, request, obj=None):
        perm = super().has_view_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.dancingparty_manager'):
            if obj:
                perm = obj.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = True
        return perm

    def has_change_permission(self, request: HttpRequest, obj: Event = None):
        perm = super().has_change_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.dancingparty_manager'):
            if obj:
                perm = obj.managers.filter(pk=request.user.pk).count() > 0
        return perm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.dancingparty_manager'):
            qs = qs.filter(managers__in=[request.user])
        return qs

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        my_urls = [
            path(
                '<int:party_pk>/registrations/<int:pk>',
                self.admin_site.admin_view(DancingPartyRegistrationTooglePaidView.as_view()),
                name='%s_%s_toggle_paid' % info
            )
        ]
        urls = my_urls + urls
        return urls


@admin.register(DancingPartyRegistration)
class DancingPartyRegistrationAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'guarantor')
    change_form_template = "cla_ticketing/admin/partyregistration_view.html"
    event = None

    def get_registration_type(self, request: HttpRequest, obj: DancingPartyRegistration):
        if obj is not None and obj.pk is not None:
            if obj.is_staff:
                return "staff"
            else:
                if obj.student_status == DancingPartyRegistration.StudentStatus.CONTRIBUTOR:
                    return "contributor"
                return "non_contributor"
        if request.method == "POST":
            return request.POST['registration_type']  # Different name to not collide with DancingPartyRegistration.type
        else:
            return request.GET['type']

    def get_fields(self, request, obj=None):
        registration_type = self.get_registration_type(request, obj)
        print(registration_type)
        if registration_type == "contributor":
            return 'user', 'type', 'home'
        elif registration_type == "non_contributor":
            return 'first_name', 'last_name', 'birthdate', 'home', 'type', 'guarantor'
        elif registration_type == "staff":
            return 'user', 'staff_description'
        raise Http404()

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        registration_type = self.get_registration_type(request, obj)
        party = get_object_or_404(DancingParty, pk=request.GET.get('dancingparty'))

        # Update context with custom properties
        context.update({
            "title": "Inscrire un " + {'contributor': "cotisant", 'non_contributor': "non cotisant", 'staff': "staffeur"}.get(registration_type),
            "type": registration_type,
            "party_opts": DancingParty._meta,
            "party": party
        })

        print(context)

        # Set all form field to required
        form = context.get('adminform').form
        for field in form.fields.values():
            field.required = True
        # Customize some field
        if 'user' in form.fields.keys():
            form.fields['user'].label = "Étudiant"
            form.fields['user'].help_text = ""

        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_party_from_request(self, request):
        party = get_object_or_404(DancingParty, pk=request.GET.get('dancingparty', None))
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and party.managers.filter(pk=request.user.pk).count() == 0:
            raise PermissionDenied()
        return party

    def save_model(self, request, obj: DancingPartyRegistration, form, change):
        registration_type = self.get_registration_type(request, obj)

        if not change:
            obj.created_by = request.user
        obj.student_status = DancingPartyRegistration.StudentStatus.CONTRIBUTOR if obj.user else DancingPartyRegistration.StudentStatus.NON_CONTRIBUTOR
        if obj.student_status == DancingPartyRegistration.StudentStatus.CONTRIBUTOR:
            obj.first_name = obj.user.first_name
            obj.last_name = obj.user.last_name
            obj.email = obj.user.email
            obj.phone = obj.user.infos.phone
            obj.birthdate = obj.user.infos.birthdate
        obj.is_staff = registration_type == "staff"
        obj.dancing_party = self.get_party_from_request(request)
        super().save_model(request, obj, form, change)

    def response_post_save_add(self, request, obj: DancingPartyRegistration):
        return redirect("admin:cla_ticketing_dancingparty_change", obj.dancing_party.pk)

    def response_post_save_change(self, request, obj: DancingPartyRegistration):
        return redirect("admin:cla_ticketing_dancingparty_change", obj.dancing_party.pk)

    def response_delete(self, request, obj_display, obj_id):
        return redirect("admin:cla_ticketing_dancingparty_change", self.get_party_from_request(request).pk)

    def get_model_perms(self, request):
        return {}

    def has_add_permission(self, request):
        perm = super().has_add_permission(request)
        if request.user.has_perm('cla_ticketing.dancingparty_manager'):
            perm = True
        return perm

    def has_view_permission(self, request: HttpRequest, obj: DancingPartyRegistration = None):
        perm = super().has_view_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.dancingparty_manager'):
            if obj:
                perm = obj.dancing_party.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = False
        return perm

    def has_change_permission(self, request: HttpRequest, obj: DancingPartyRegistration = None):
        perm = super().has_change_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.dancingparty_manager'):
            if obj:
                perm = obj.dancing_party.managers.filter(pk=request.user.pk).count() > 0
        return perm

    def has_delete_permission(self, request: HttpRequest, obj: DancingPartyRegistration = None):
        perm = super().has_delete_permission(request, obj)
        if not request.user.has_perm('cla_ticketing.add_dancingparty') and request.user.has_perm('cla_ticketing.dancingparty_manager'):
            if obj:
                perm = obj.dancing_party.managers.filter(pk=request.user.pk).count() > 0
            else:
                perm = False
        return perm
