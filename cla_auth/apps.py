from django.apps import AppConfig

class ClaAuthConfig(AppConfig):
    name = 'cla_auth'

    def ready(self):
        # Enregistrement des fonctions de l'application liées aux signaux
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save
        from cla_auth.signals import send_activation_email

        post_save.connect(send_activation_email, sender=User)  # Envoie d'un mail lors de la création d'un compte
