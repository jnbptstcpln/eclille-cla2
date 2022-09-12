from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, Http404
from django.shortcuts import resolve_url, get_object_or_404
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from cla_lyfpay.models import *


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    class WalletFilter(SimpleListFilter):
        title = 'wallet'
        parameter_name = 'wallet'

        def lookups(self, request, model_admin):
            # Retrieve wallet with at least one payment in the last month
            return [
                (r.pk, str(r))
            for r in Wallet.objects.filter(payments__created_at__gte=timezone.now() - timedelta(hours=1)).order_by('-created_at').distinct()]

        def queryset(self, request, queryset):
            raw_val = self.value()
            if raw_val:
                return queryset.filter(wallet__pk=raw_val)
            return queryset
        
    ordering = ('-created_at',)
    list_display = ['__str__', 'get_amount_display', 'created_at', 'created_by', 'lyfpay_status', 'wallet']
    search_fields = ['lyfpay_shop_reference', 'created_by__username']
    list_filter = [WalletFilter]
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


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    pass