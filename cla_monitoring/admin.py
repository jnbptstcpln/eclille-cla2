from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .models import Error


class ResolvedFilter(admin.SimpleListFilter):
    title = "statut"
    parameter_name = "statut"

    def lookups(self, request, model_admin):
        return [("a_traiter", "À traiter"), ("reglee", "Réglée")]

    def queryset(self, request, queryset):
        if self.value() == "a_traiter":
            return queryset.filter(resolved_on__isnull=True)
        if self.value() == "reglee":
            return queryset.filter(resolved_on__isnull=False)
        return queryset


@admin.register(Error)
class ErrorAdmin(admin.ModelAdmin):
    """
    Journal des erreurs, rempli automatiquement (cla_monitoring.handlers.DatabaseHandler).
    On ne peut que le consulter, marquer des erreurs comme réglées et supprimer des lignes.
    """

    list_display = ("last_seen", "title", "location", "count", "status_badge")
    list_filter = (ResolvedFilter, "last_seen")
    search_fields = ("title", "location", "path")
    date_hierarchy = "last_seen"
    fields = ("title", "status_badge", "count", "first_seen", "last_seen", "location", "path", "user",
              "logger", "traceback_display")
    readonly_fields = fields
    actions = ["mark_resolved"]

    @admin.display(description="statut")
    def status_badge(self, obj):
        if obj.resolved_on:
            return format_html('<strong style="color: #2e7d32">Réglée</strong>')
        return format_html('<strong style="color: #c62828">À traiter</strong>')

    @admin.display(description="détail (dernière occurrence)")
    def traceback_display(self, obj):
        if not obj.traceback:
            return "-"
        return format_html('<pre style="white-space: pre-wrap; font-size: 0.75rem">{}</pre>', obj.traceback)

    @admin.action(description="Marquer comme réglées", permissions=["resolve"])
    def mark_resolved(self, request, queryset):
        count = queryset.filter(resolved_on__isnull=True).update(resolved_on=timezone.now())
        self.message_user(request, f"{count} erreur(s) marquée(s) comme réglée(s).", messages.SUCCESS)

    def has_resolve_permission(self, request):
        return request.user.has_perm("cla_monitoring.change_error")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
