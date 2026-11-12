from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from .models import Mail
from .sending import deliver, send

STATUS_COLORS = {Mail.Status.SENT: "#2e7d32", Mail.Status.PENDING: "#ef6c00", Mail.Status.FAILED: "#c62828"}


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    """
    Journal en lecture seule : les lignes sont créées par cla_mail.sending, jamais à la main.
    Avec la permission « Peut renvoyer un mail » (ou en superuser), on peut renvoyer des mails
    et s'envoyer un mail de test.
    """

    list_display = ("created_on", "kind", "recipient", "user", "subject", "status_badge")
    list_filter = ("status", "kind", "created_on")
    search_fields = ("recipient", "subject", "user__username", "user__first_name", "user__last_name")
    date_hierarchy = "created_on"
    list_select_related = ("user",)
    fields = ("created_on", "sent_on", "kind", "recipient", "user", "target_display", "subject", "status",
              "attempts", "error")
    readonly_fields = fields
    actions = ["resend"]

    @admin.display(description="objet concerné")
    def target_display(self, obj):
        return obj.target or "-"

    @admin.display(description="statut", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<strong style="color: {}">{}</strong>',
            STATUS_COLORS.get(obj.status, "inherit"), obj.get_status_display(),
        )

    @admin.action(description="Renvoyer les mails sélectionnés", permissions=["send"])
    def resend(self, request, queryset):
        # Le contenu est reconstruit (nouveau lien, code à jour) ; le quota du jour n'est pas vérifié
        results = [deliver(mail) for mail in queryset]
        if all(results):
            self.message_user(request, f"{len(results)} mail(s) renvoyé(s).", messages.SUCCESS)
        else:
            self.message_user(
                request, f"{results.count(False)} mail(s) sur {len(results)} n'ont pas pu être renvoyés : "
                         "voir la colonne « erreur » de chaque mail.", messages.ERROR,
            )

    def send_test(self, request):
        if not self.has_send_permission(request):
            raise PermissionDenied
        if not request.user.email:
            self.message_user(request, "Votre compte n'a pas d'adresse mail.", messages.ERROR)
        else:
            mail = send(Mail.Kind.TEST, user=request.user)
            if mail.status == Mail.Status.SENT:
                self.message_user(request, f"Mail de test envoyé à {mail.recipient}.", messages.SUCCESS)
            else:
                self.message_user(request, f"Le mail de test n'a pas pu être envoyé : {mail.error}", messages.ERROR)
        return redirect("admin:cla_mail_mail_changelist")

    def get_urls(self):
        return [
            path("test/", self.admin_site.admin_view(require_POST(self.send_test)), name="cla_mail_mail_test"),
        ] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), "can_send_mail": self.has_send_permission(request)}
        return super().changelist_view(request, extra_context)

    def has_send_permission(self, request):
        return request.user.has_perm("cla_mail.send_mail")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
