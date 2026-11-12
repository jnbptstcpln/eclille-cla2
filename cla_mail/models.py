from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Mail(models.Model):
    """
    Journal des mails envoyés par le site : une ligne par mail et par destinataire.

    Le contenu n'est volontairement pas enregistré : il contient des liens et des codes secrets
    (activation de compte, réinitialisation de mot de passe, code de validation). Il est reconstruit
    à partir de l'objet concerné (`target`) quand un mail en attente part ou est renvoyé.
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
        PENDING = "pending", "En attente"
        FAILED = "failed", "Échec"

    class Meta:
        verbose_name = "mail"
        verbose_name_plural = "journal des mails"
        ordering = ("-created_on",)
        permissions = [("send_mail", "Peut renvoyer un mail et envoyer un mail de test")]

    created_on = models.DateTimeField("créé le", auto_now_add=True, db_index=True)
    sent_on = models.DateTimeField("envoyé le", null=True, blank=True)
    kind = models.CharField("type", max_length=32, choices=Kind.choices)
    recipient = models.EmailField("destinataire", blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="utilisateur", related_name="+",
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    subject = models.CharField("sujet", max_length=255, blank=True)
    status = models.CharField("statut", max_length=16, choices=Status.choices, db_index=True)
    error = models.TextField("erreur", blank=True)
    attempts = models.PositiveSmallIntegerField("tentatives d'envoi", default=0)

    # Objet concerné (inscription, événement, réservation…), pour reconstruire le contenu
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.get_kind_display()} → {self.recipient}"
