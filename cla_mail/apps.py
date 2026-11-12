from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class ClaMailConfig(AppConfig):
    name = "cla_mail"
    verbose_name = "Mails"

    def ready(self):
        # Charge les fichiers mails.py des apps, qui déclarent le contenu de chaque type de mail
        autodiscover_modules("mails")
