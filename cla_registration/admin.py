from django.contrib import admin
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import resolve_url, get_object_or_404
from django.urls import path
from django.utils.safestring import mark_safe

from .models import RegistrationSession, Registration
from .views.admin import RegistrationValidationView


@admin.register(RegistrationSession)
class RegistrationSessionAdmin(admin.ModelAdmin):
    class RegistrationInline(admin.TabularInline):
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
                    f"<a id='change_id_registrations-{obj.pk}-registration' title='Voir l\\'utilisateur' target='_blank' href='{resolve_url('admin:auth_user_change', obj.account.pk)}'><img src='/static/admin/img/icon-viewlink.svg' alt='Voir'></a>"
                )
            return mark_safe(
                f"<a id='change_id_registrations-{obj.pk}-registration' title='Voir l\\'inscription' target='_blank' href='{resolve_url('admin:cla_registration_registrationsession_registration', obj.session.pk, obj.pk)}'><img src='/static/admin/img/icon-viewlink.svg' alt='Voir'></a>"
            )

        edit_button.short_description = "edit_button"

    fieldsets = [
        [
            "Informations pratiques",
            {
                'fields': (
                    ('school_year',),
                    ('date_start', 'date_end'),
                )
            }
        ],

    ]
    readonly_fields = ['pumpkin_configuration', 'statistics', 'link_sharing_alumni']

    list_display = ("school_year", "date_start", "date_end", "number_of_registrations")

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        if obj is not None:
            return inlines + [self.RegistrationInline]
        return inlines

    def get_fieldsets(self, request, obj=None):
        _fieldsets = super().get_fieldsets(request, obj)
        fieldsets = _fieldsets

        if request.user.has_perm("cla_registration.registrationsession_change"):
            fieldsets += [
                [
                    "Partage des informations d'adhésion",
                    {
                        'fields': ('link_sharing_alumni',),
                        'classes': ('collapse',),
                    }
                ],
                [
                    "Configuration de la plateforme de paiement",
                    {
                        'fields': ('pumpkin_configuration',),
                        'classes': ('collapse',),
                    }
                ],
                [
                    "Lien vers les billeteries",
                    {
                        'fields': ('ticketing_href_centrale_pack', 'ticketing_href_centrale_cla', 'ticketing_href_centrale_dd_pack', 'ticketing_href_centrale_dd_cla', 'ticketing_href_iteem_pack', 'ticketing_href_iteem_cla'),
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
                        'classes': ('collapse',),
                    }
                ]
            ]
        return fieldsets

    def pumpkin_configuration(self, obj: RegistrationSession):
        if obj.pk:  # Check if the object was created
            return mark_safe(
                render_to_string(
                    "cla_registration/admin/pumpkin_configuration.html",
                    {
                        'session': obj
                    }
                )
            )
        else:
            return ""
    pumpkin_configuration.short_description = ''

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
        print('%s_%s_registration' % info)
        urls = super().get_urls()
        my_urls = [
            path(
                '<uuid:session_pk>/registrations/<uuid:registration_pk>',
                self.admin_site.admin_view(RegistrationValidationView.as_view()),
                name='%s_%s_registration' % info
            )
        ]
        urls = my_urls + urls
        return urls

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        return super().render_change_form(request, context, add, change, form_url, obj)
