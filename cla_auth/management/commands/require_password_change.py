from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from cla_auth.models import PasswordChange


class Command(BaseCommand):
    help = (
        "À utiliser après un incident de sécurité : oblige tous les utilisateurs (superusers compris) "
        "à choisir un nouveau mot de passe à leur prochaine connexion. Aucun mail n'est envoyé."
    )

    def handle(self, *args, **options):
        PasswordChange.objects.all().delete()
        count = User.objects.exclude(password="").exclude(password__startswith=UNUSABLE_PASSWORD_PREFIX).count()
        self.stdout.write(f"{count} utilisateur(s) devront choisir un nouveau mot de passe à leur prochaine connexion.")
