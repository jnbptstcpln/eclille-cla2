from django.conf import settings
from django.db import models


class Mail(models.Model):
    """
    Journal des mails envoyés par le site : une ligne par mail et par destinataire.

    Le contenu n'est volontairement pas enregistré : il contient des liens et des codes secrets
    (activation de compte, réinitialisation de mot de passe, code de validation).
    """

    class Kind(models.TextChoices):
        ACTIVATION = "activation", "Activation de compte"
        PASSWORD_RESET = "password_reset", "Mot de passe oublié"
        ACCOUNT_VALIDATION = "account_validation", "Code de validation du compte"
        EVENT_TO_VALIDATE = "event_to_validate", "Événement à valider"
        RESERVATION_TO_VALIDATE = "reservation_to_validate", "Réservation à valider"
        TEST = "test", "Mail de test"

    class Status(models.TextChoices):
        SENT = "sent", "Envoyé"
        FAILED = "failed", "Échec"

    class Meta:
        verbose_name = "mail"
        verbose_name_plural = "journal des mails"
        ordering = ("-created_on",)

    created_on = models.DateTimeField("créé le", auto_now_add=True, db_index=True)
    sent_on = models.DateTimeField("envoyé le", null=True, blank=True)
    kind = models.CharField("type", max_length=32, choices=Kind.choices)
    recipient = models.EmailField("destinataire")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="utilisateur", related_name="+",
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    subject = models.CharField("sujet", max_length=255)
    status = models.CharField("statut", max_length=16, choices=Status.choices)
    error = models.TextField("erreur", blank=True)

    def __str__(self):
        return f"{self.get_kind_display()} → {self.recipient}"
