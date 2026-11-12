from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from cla_monitoring.models import Error


class Command(BaseCommand):
    help = (
        "Tâches régulières du site, à lancer toutes les heures (tâche planifiée Coolify) : "
        "envoi des mails en attente, nettoyage des journaux."
    )

    def handle(self, *args, **options):
        call_command("send_pending_mails", stdout=self.stdout)

        limit = timezone.now() - timezone.timedelta(days=settings.ERROR_RETENTION_DAYS)
        purged, _ = Error.objects.filter(resolved_on__isnull=False, last_seen__lt=limit).delete()
        self.stdout.write(f"{purged} erreur(s) réglée(s) effacée(s) du journal.")
