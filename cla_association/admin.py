
from django.contrib import admin

from cla_association.models import Association, AssociationMember, AssociationLink, HandoverFolder


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):

    class MemberInline(admin.TabularInline):
        model = AssociationMember
        autocomplete_fields = ['user']
        extra = 0

    class LinkInline(admin.TabularInline):
        model = AssociationLink
        extra = 0

    inlines = [MemberInline, LinkInline]


@admin.register(HandoverFolder)
class HandoverFolderAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'validated'
    ]
    search_fields = ['association']
