import csv
from datetime import timedelta
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.shortcuts import resolve_url, get_object_or_404
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils import timezone

from cla_web.utils import current_school_year
from .models import RegistrationSession, Registration, ImageRightAgreement
from .views.admin import RegistrationValidationView, RegistrationSessionExportView


@admin.register(RegistrationSession)
class RegistrationSessionAdmin(admin.ModelAdmin):
    class RegistrationInline(TabularInlinePaginated):
        fields = ['last_name', 'first_name', 'has_pack', 'type', 'datetime_registration', 'is_linked_to_an_account', 'edit_button']
        readonly_fields = ['last_name', 'first_name', 'datetime_registration', 'is_linked_to_an_account', 'edit_button', 'has_pack', 'type']
        model = Registration
        classes = []
        max_num = 0
        extra = 0
        ordering = "last_name",

        can_delete = False
        template = "cla_registration/admin/change_registrations.html"

        def is_linked_to_an_account(self, obj: Registration):
            return obj.account is not None
        is_linked_to_an_account.short_description = "Compte créé ?"
        is_linked_to_an_account.boolean = True

        def has_pack(self, obj: Registration):
            return obj.pack
        has_pack.short_description = "Pack ?"
        has_pack.boolean = True

        def type(self, obj: Registration):
            return obj.type
        type.short_description = "Type"

        def edit_button(self, obj: Registration):
            if obj.account is not None:
                return mark_safe(
                    f"<a id='change_id_registrations-{obj.pk}-registration' title='Voir l\\'utilisateur' href='{resolve_url('admin:auth_user_change', obj.account.pk)}'><img src='/static/admin/img/icon-viewlink.svg' alt='Voir'></a>"
                )
            return mark_safe(
                f"<a id='change_id_registrations-{obj.pk}-registration' title='Voir l\\'inscription' href='{resolve_url('admin:cla_registration_registrationsession_registration', obj.session.pk, obj.pk)}'><img src='/static/admin/img/icon-viewlink.svg' alt='Voir'></a>"
            )
        edit_button.short_description = "edit_button"

        def get_queryset(self, request):
            queryset = super().get_queryset(request)
            if request.GET.get('registration_search') is not None:
                queryset = queryset.filter(Q(last_name__icontains=request.GET.get('registration_search')) | Q(first_name__icontains=request.GET.get('registration_search')))
            return queryset

    readonly_fields = ['statistics', 'link_sharing_alumni']
    list_display = ("school_year", "date_start", "date_end", "number_of_registrations")
    change_form_template = "cla_registration/admin/change_registrationsession.html"

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        if obj is not None:
            return inlines + [self.RegistrationInline]
        return inlines

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            [
                "Informations pratiques",
                {
                    'fields': (
                        ('school_year',),
                        ('date_start', 'date_end'),
                    ),
                }
            ]
        ]
        if request.user.has_perm("cla_registration.change_registrationsession"):
            fieldsets += [
                [
                    "Partage des informations d'adhésion",
                    {
                        'fields': ('link_sharing_alumni',),
                        'classes': ('collapse',),
                    }
                ],                
                [
                    "Lien vers les billeteries",
                    {
                        'fields': (
                            'ticketing_href_centrale_pack',
                            'ticketing_href_centrale_cla',
                            'ticketing_href_centrale_dd_pack',
                            'ticketing_href_centrale_dd_cla',
                            'ticketing_href_iteem_pack',
                            'ticketing_href_iteem_cla',
                            'ticketing_href_enscl_cla'
                        ),
                        'classes': ('collapse',),
                    }
                ]
            ]

        if obj is not None:
            fieldsets += [
                [
                    "Statistiques",
                    {
                        'fields': ('statistics',),
                        'classes': ('collapse',)
                    }
                ]
            ]

        return fieldsets

    def number_of_registrations(self, obj: RegistrationSession):
        return obj.registrations.count()
    number_of_registrations.short_description = 'Nombre d\'adhésion'

    def statistics(self, obj: RegistrationSession):
        if obj.pk:  # Check if the object was created
            return mark_safe(
                render_to_string(
                    "cla_registration/admin/stats.html",
                    {
                        'session': obj
                    }
                )
            )
        return ""
    statistics.short_description = 'Statistiques'

    def link_sharing_alumni(self, obj: RegistrationSession):
        return mark_safe(
            (
                "<label style='float:none;width:100%'>Transmettez le lien suivant aux représentants de Centrale Lille Alumni pour leur permettre d'accéder à la liste des adhérents ayant accepté de partager leurs informations personnelles avec Centrale Lille Alumni</label>"
                "<input style='margin-right: .5rem' class='vTextField' value='{link_sharing_alumni}' id='id_link_sharing_alumni'>"
                "<a class='button' onclick='document.getElementById(\"id_link_sharing_alumni\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
            ).format(link_sharing_alumni=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_registration:registration_sharing_alumni', obj.pk, obj.sharing_uuid_alumni)}")
        )
    link_sharing_alumni.short_description = ''

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        my_urls = [
            path(
                '<uuid:session_pk>/registrations/<uuid:registration_pk>',
                self.admin_site.admin_view(RegistrationValidationView.as_view()),
                name='%s_%s_registration' % info
            ),
            path(
                '<uuid:session_pk>/registrations/export',
                self.admin_site.admin_view(RegistrationSessionExportView.as_view()),
                name='%s_%s_export' % info
            )
        ]
        urls = my_urls + urls
        return urls

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(ImageRightAgreement)
class ImageRightAgreementAdmin(admin.ModelAdmin):

    class YearFilter(SimpleListFilter):
        title = 'année'
        parameter_name = 'promo'

        def lookups(self, request, model_admin):
            y = current_school_year()
            return [(y-i, y-i) for i in range(4)]

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(created_on__year=self.value())
            else:
                return queryset

    list_filter = (YearFilter,)

    fields = (
        'created_on',
        'account',
        ('first_name', 'last_name'),
        'birthdate',
        'email_school',
        'file'
    )
    readonly_fields = ('created_on', 'account', 'file')
    list_display = ("fullname", "created_on", "account")

    def account(self, obj: ImageRightAgreement):
        user = User.objects.filter(infos__email_school=obj.email_school, date_joined__year=obj.created_on.year).first()
        if user:
            return mark_safe(f"<a href='{resolve_url('admin:auth_user_change', user.pk)}'>{user.first_name} {user.last_name}</a>")
        return "Aucun compte correspondant"

    account.short_description = "Compte lié"


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    
    class SessionFilter(SimpleListFilter):
        title = 'session'
        parameter_name = 'session'

        def lookups(self, request, model_admin):
            return [
                (r.pk, str(r))
            for r in RegistrationSession.objects.filter(date_start__gte=timezone.now() - timedelta(days=365*5))]

        def queryset(self, request, queryset):
            raw_val = self.value()
            if raw_val:
                return queryset.filter(session__pk=raw_val)
            return queryset
    
    class SchoolFilter(SimpleListFilter):
        title = 'école'
        parameter_name = 'school'

        def lookups(self, request, model_admin):
            return Registration.SchoolDomains.choices

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(school=self.value())
            else:
                return queryset
    
    class AccountFilter(SimpleListFilter):
        title = 'compte créé'
        parameter_name = 'account'

        def lookups(self, request, model_admin):
            return [(1, "Compte créé"), (2, "Compte non créé")]

        def queryset(self, request, queryset):
            raw_val = self.value()
            if raw_val is not None:
                val = int(raw_val)
                if val == 1:
                    return queryset.filter(account__isnull=False)
                elif val == 2:
                    return queryset.filter(account__isnull=True)
            return queryset
        
    list_filter = (SessionFilter, SchoolFilter, AccountFilter)
    list_display = ['__str__', 'has_pack', 'type', 'datetime_registration', 'is_linked_to_an_account']
    search_fields = ('first_name', 'last_name', 'email', 'email_school')
    
    def is_linked_to_an_account(self, obj: Registration):
            return obj.account is not None
    is_linked_to_an_account.short_description = "Compte créé ?"
    is_linked_to_an_account.boolean = True

    def has_pack(self, obj: Registration):
        return obj.pack
    has_pack.short_description = "Pack ?"
    has_pack.boolean = True

    def has_module_permission(self, request):
        return False

    def has_delete_permission(self, request: HttpRequest, obj = None) -> bool:
        if obj:
            if obj.account:
                return False
        return super().has_delete_permission(request, obj)