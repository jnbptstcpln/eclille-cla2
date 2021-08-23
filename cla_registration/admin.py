from django.contrib import admin
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .models import RegistrationSession, Registration


@admin.register(RegistrationSession)
class RegistrationSessionAdmin(admin.ModelAdmin):

    class RegistrationInline(admin.TabularInline):
        fields = ['last_name', 'first_name', 'datetime_registration', 'edit_button']
        readonly_fields = ['last_name', 'first_name', 'datetime_registration', 'edit_button']
        model = Registration
        classes = []
        max_num = 0

        can_delete = False
        template = "cla_registration/admin/change_registrations.html"

        def edit_button(self, obj: Registration):
            return mark_safe(
                f"<a id='change_id_registrations-{obj.id}-registration' class='related-widget-wrapper-link change-related' data-href-template='/admin/cla_registration/registration/__fk__/change/?_to_field=id&amp;_popup=1' title='Modifier' href='/admin/cla_registration/registration/{obj.id}/change/?_to_field=id&amp;_popup=1&amp;session={obj.session.pk}' onclick='django.jQuery(this).parents(\"tr\").children().css(\"background-color\", \"rgb(255,255,205,.25)\")'><img src='/static/admin/img/icon-changelink.svg' alt='Modification'></a>"+
                f"<a id='delete_id_registrations-{obj.id}-registration' class='related-widget-wrapper-link delete-related' data-href-template='/admin/cla_registration/registration/__fk__/delete/?_to_field=id&amp;_popup=1' title='Supprimer l\\'inscription' href='/admin/cla_registration/registration/{obj.id}/delete/?_to_field=id&amp;_popup=1' onclick='django.jQuery(this).parents(\"tr\").children().css(\"background-color\", \"rgb(255,0,0,.25)\")'><img src='/static/admin/img/icon-deletelink.svg' alt='Supprimer'></a>"
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
        [
            "Configuration de la plateforme de paiement",
            {
                'fields': ('pumpking_configuration',),
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
    readonly_fields = ['pumpking_configuration']
    inlines = [RegistrationInline]

    def pumpking_configuration(self, obj: RegistrationSession):
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
    pumpking_configuration.short_description = ''


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    pass
