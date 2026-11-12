"""
Alertes affichées dans l'en-tête de l'admin (pastille rouge), pour que les admins voient
tout de suite qu'il y a un problème sans aller fouiller dans les journaux.
"""
from django.urls import reverse
from django.utils import timezone

from cla_mail.models import Mail

from .models import Error

# Un mail en échec reste signalé pendant cette durée, ou jusqu'à ce qu'il soit renvoyé avec succès
FAILED_MAILS_ALERT_DAYS = 7


def admin_alerts(user):
    """Liste de (texte, lien) pour les journaux que l'utilisateur a le droit de voir."""
    alerts = []
    if user.has_perm("cla_monitoring.view_error"):
        count = Error.objects.filter(resolved_on__isnull=True).count()
        if count:
            label = f"{count} erreur{'s' if count > 1 else ''} à traiter"
            alerts.append((label, reverse("admin:cla_monitoring_error_changelist") + "?statut=a_traiter"))
    if user.has_perm("cla_mail.view_mail"):
        since = timezone.now() - timezone.timedelta(days=FAILED_MAILS_ALERT_DAYS)
        count = Mail.objects.filter(status=Mail.Status.FAILED, created_on__gte=since).count()
        if count:
            label = f"{count} mail{'s' if count > 1 else ''} en échec"
            alerts.append((label, reverse("admin:cla_mail_mail_changelist") + "?status__exact=failed"))
    return alerts
