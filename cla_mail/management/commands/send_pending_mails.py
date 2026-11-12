from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from cla_mail.models import Mail
from cla_mail.sending import deferrable_budget, deliver

# Au-delà, un mail en attente qui échoue passe en « Échec » (adresse invalide, objet supprimé…)
MAX_ATTEMPTS = 3


class Command(BaseCommand):
    help = (
        "Envoie les mails en attente tant que le quota du jour le permet, "
        "puis efface du journal les mails de plus de MAIL_RETENTION_DAYS jours. "
        "À lancer toutes les heures (tâche planifiée Coolify)."
    )

    def handle(self, *args, **options):
        sent = 0
        for mail in Mail.objects.filter(status=Mail.Status.PENDING).order_by("created_on"):
            if deferrable_budget() <= 0:
                break
            if deliver(mail):
                sent += 1
                continue
            if mail.attempts < MAX_ATTEMPTS:
                # Sans doute un refus de Brevo (quota, panne) : on réessaiera au prochain passage
                mail.status = Mail.Status.PENDING
                mail.save()
            break

        pending = Mail.objects.filter(status=Mail.Status.PENDING).count()
        limit = timezone.now() - timezone.timedelta(days=settings.MAIL_RETENTION_DAYS)
        purged, _ = Mail.objects.filter(created_on__lt=limit).exclude(status=Mail.Status.PENDING).delete()
        self.stdout.write(f"{sent} mail(s) envoyé(s), {pending} encore en attente, {purged} ancien(s) effacé(s) du journal.")
