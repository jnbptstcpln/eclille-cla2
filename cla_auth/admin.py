from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.shortcuts import resolve_url
from django.utils.html import mark_safe, escape
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from .models import *
from cla_auth.forms.admin_user_form import UserCreationForm

# Remove default User management interface
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserAdmin):
    class UserInfosInline(admin.StackedInline):
        model = UserInfos
        verbose_name = "Informations complémentaires"
        fields = (
            ('email_school', 'phone'),
            ('promo', 'cursus'),
            'birthdate',
            ('activated_on', 'valid_until'),
            'account_type'
        )
        readonly_fields = 'activated_on', 'valid_until'
        extra = 1
        min_num = 1
        can_delete = False

    class MembershipInline(admin.StackedInline):
        model = UserMembership
        fields = (
            ('amount', 'paid_on', 'paid_by'),
            ('refunded', 'refunded_amount', 'refunded_on')
        )
        extra = 0
        min_num = 0

    fieldsets = (
        (
            _('Personal info'),
            {
                'fields': (('first_name', 'last_name'), 'email')
            }
        ),
        (
            "Information de connexion",
            {
                'fields': ('username', 'password', ('last_login', 'date_joined')),
                'classes': ('collapse',),
            }
        ),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
                'classes': ('collapse',),
            }
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (('first_name', 'last_name'), 'email'),
        }),
    )
    readonly_fields = 'username', 'last_login', 'date_joined'
    inlines = [
        UserInfosInline,
        MembershipInline,
    ]
    list_display = ('username', 'first_name', 'last_name', 'email_school', 'is_activated', 'is_validated')
    list_filter = ('is_staff',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    add_form = UserCreationForm

    def email_school(self, obj: User):
        return obj.infos.email_school
    email_school.short_description = 'Email école'

    def is_activated(self, obj: User):
        return obj.infos.activated_on is not None
    is_activated.short_description = 'Compté activé'
    is_activated.boolean = True

    def is_validated(self, obj: User):
        return obj.infos.valid_until is not None and obj.infos.valid_until > timezone.now()
    is_validated.short_description = 'Compte validé'
    is_validated.boolean = True
