
from django.contrib import admin

from cla_association.models import Association, AssociationMember, AssociationLink


@admin.register(Association)
class WebsiteAdmin(admin.ModelAdmin):

    class MemberInline(admin.TabularInline):
        model = AssociationMember
        autocomplete_fields = ['user']
        extra = 0

    class LinkInline(admin.TabularInline):
        model = AssociationLink
        extra = 0

    inlines = [MemberInline, LinkInline]
