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

from cla_lyfpay.models import *


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'get_amount_display', 'created_at', 'created_by', 'lyfpay_status', 'wallet']
    readonly_fields = [
        'wallet',
        'created_by',
        'origin',
        'reference',
        'lyfpay_shop_reference',
        'lyfpay_shop_order_reference',
        'lyfpay_id',
        'lyfpay_amount',
        'lyfpay_status',
        'lyfpay_updated_at'
    ]

    def get_amount_display(self, obj: Payment):
        return obj.amount_display
    get_amount_display.short_description = 'Montant'
