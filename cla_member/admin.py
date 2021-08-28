
from django.contrib import admin

from cla_member.models import Website


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    pass
