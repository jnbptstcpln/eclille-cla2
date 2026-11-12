from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone


class Error(models.Model):
    """
    Journal des erreurs du site : pages qui plantent (erreur 500) et erreurs signalées par le code
    (logger.error / logger.exception). Les erreurs identiques sont regroupées sur une seule ligne,
    avec leur nombre d'occurrences.

    On n'y enregistre jamais ce que l'utilisateur a envoyé (formulaires, mots de passe) :
    seulement la page, l'utilisateur et l'endroit du code.
    """

    class Meta:
        verbose_name = "erreur"
        verbose_name_plural = "journal des erreurs"
        ordering = ("-last_seen",)

    fingerprint = models.CharField(max_length=64, unique=True, editable=False)
    title = models.CharField("erreur", max_length=255)
    location = models.CharField("endroit du code", max_length=255, blank=True)
    logger = models.CharField("source", max_length=100, blank=True)
    traceback = models.TextField("détail (dernière occurrence)", blank=True)
    path = models.CharField("page (dernière occurrence)", max_length=255, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="utilisateur (dernière occurrence)", related_name="+",
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    count = models.PositiveIntegerField("occurrences", default=1)
    first_seen = models.DateTimeField("première fois", auto_now_add=True)
    last_seen = models.DateTimeField("dernière fois", db_index=True)
    resolved_on = models.DateTimeField("réglée le", null=True, blank=True)

    def __str__(self):
        return self.title

    @classmethod
    def record(cls, fingerprint, **fields):
        """Ajoute une occurrence. Une erreur « réglée » qui revient repasse « à traiter »."""
        now = timezone.now()
        updated = cls.objects.filter(fingerprint=fingerprint).update(
            count=F("count") + 1, last_seen=now, resolved_on=None, **fields,
        )
        if not updated:
            cls.objects.create(fingerprint=fingerprint, last_seen=now, **fields)
