from django.apps import AppConfig


class ClaAuthConfig(AppConfig):
    name = 'cla_auth'
    verbose_name = "Gestion de l'authentification"

    def ready(self):
        from . import checks  # noqa: F401  Vérification des services : manage.py check --database default
        # Enregistrement des fonctions de l'application liées aux signaux
        from .models import UserInfos
        from django.db.models.signals import post_save
        from django.contrib.auth.models import User
        from cla_auth.signals import send_activation_email, record_password_change

        post_save.connect(send_activation_email, sender=UserInfos)  # Envoie d'un mail lors de la création d'un compte
        post_save.connect(record_password_change, sender=User)  # Date du dernier changement de mot de passe
