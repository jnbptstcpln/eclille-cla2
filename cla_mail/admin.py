from django.contrib import admin
from django.utils.html import format_html

from .models import Mail

STATUS_COLORS = {Mail.Status.SENT: "#2e7d32", Mail.Status.PENDING: "#ef6c00", Mail.Status.FAILED: "#c62828"}


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    """Journal en lecture seule : les lignes sont créées par cla_mail.sending, jamais à la main."""

    list_display = ("created_on", "kind", "recipient", "user", "subject", "status_badge")
    list_filter = ("status", "kind", "created_on")
    search_fields = ("recipient", "subject", "user__username", "user__first_name", "user__last_name")
    date_hierarchy = "created_on"
    list_select_related = ("user",)
    fields = ("created_on", "sent_on", "kind", "recipient", "user", "target_display", "subject", "status",
              "attempts", "error")
    readonly_fields = fields

    @admin.display(description="objet concerné")
    def target_display(self, obj):
        return obj.target or "-"

    @admin.display(description="statut", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<strong style="color: {}">{}</strong>',
            STATUS_COLORS.get(obj.status, "inherit"), obj.get_status_display(),
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
