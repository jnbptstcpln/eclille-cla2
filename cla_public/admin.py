from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages import admin as flatpage_admin
from django.utils.translation import gettext_lazy as _

from cla_public.forms import admin_flatpage

# Define a new FlatPageAdmin
admin.site.unregister(FlatPage)


@admin.register(FlatPage)
class FlatPageAdmin(flatpage_admin.FlatPageAdmin):
    form = admin_flatpage.FlatpageForm
    fieldsets = (
        (None, {
            'fields': ('url', 'title', 'content', 'sites'),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'registration_required',
                'template_name',
            ),
        }),
    )
