from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import resolve_url
from django.utils.html import mark_safe, escape
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from .models import *


# Remove default User management interface
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserAdmin):

    class UserInfosInline(admin.StackedInline):
        model = UserInfos
        fields = (
            'email_school',
            'phone',
            ('promo', 'cursus'),
            'birthdate',
            ('activated_on', 'valid_until')
        )
        readonly_fields = 'activated_on', 'valid_until'
        extra = 1
        min_num = 1

    class MembershipInline(admin.StackedInline):
        model = UserMembership
        fields = (
                     ('amount', 'paid_on', 'paid_by'),
                     ('refunded', 'refunded_amount', 'refunded_on')
        )
        extra = 0
        min_num = 0

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    inlines = [
        UserInfosInline,
        MembershipInline,
    ]
