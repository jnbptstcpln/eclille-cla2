import os
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_summernote.fields import SummernoteTextField

from cla_event.models import Event


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def rules(cls, instance, filename):
        return cls._path(instance, ["cla_reservation", "barbecue_rules"], filename)


class RulesManager(models.Manager):

    def last(self):
        return self.filter(available=True).order_by("-created_on").first()


class BarbecueRules(models.Model):
    objects = RulesManager()

    class Meta:
        ordering = "-created_on",
        verbose_name = "[BARBECUE] Charte du barbecue"
        verbose_name_plural = "[BARBECUE] Chartes du barbecue"

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    description = SummernoteTextField(verbose_name="Présentation", help_text="Rappelle des éléments important tel que les différents chèques de cautions")
    file = models.FileField(upload_to=FilePath.rules, blank=True, null=True, verbose_name="Fichier", help_text="De préférence au format PDF ou Excel")
    available = models.BooleanField(default=False, verbose_name="Cette version est disponible à la consultation")

    def __str__(self):
        return f"Charte {self.created_on.strftime('%Y')}"


class ReservationBarbecueManager(models.Manager):

    def to_validate(self):
        return self.filter(validated=False, sent=True).order_by('sent_on')

    def is_range_free(self, start, end):
        return self.filter(starts_on__lte=end, ends_on__gte=start, validated=True).count() == 0


class ReservationBarbecue(models.Model):

    objects = ReservationBarbecueManager()

    class Meta:
        ordering = "-starts_on",
        verbose_name = "[BARBECUE] Réservation"
        verbose_name_plural = "[BARBECUE] Réservations"

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="reservation_barbecue", null=True, blank=True, verbose_name="Réserver dans le cadre de cet événement", editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="+", null=True, blank=True, verbose_name="Réserver à titre personnel par ce cotisant", editable=False)

    description_event = SummernoteTextField(verbose_name="Description de l'événement", help_text="Précisez ici comment va être organisé votre événement, quelles activités seront proposées et quels seront vos besoins (électrique, équipements particulier, ...)")
    description_user = SummernoteTextField(verbose_name="Description de l'événement", help_text="Précisez ici dans quel cadre est organisée cette réservation et le nombre de personnes participantes")

    start_date = models.DateField(verbose_name="Date de début de l'installation", help_text="Indiquez ici la date à partir de laquelle vous souhaitez occuper le lieu pour l'installation")
    start_time = models.TimeField(verbose_name="Heure de début de l'installation", help_text="Au format HH:MM (par exemple 18:30)")
    end_time = models.TimeField(verbose_name="Heure de fin du rangement", help_text="Au format HH:MM (par exemple 01:00), elle correspond au moment où vous devez avoir rangé et nettoyé le lieu")
    multiple_days = models.BooleanField(default=False, verbose_name="L'événement se déroule sur plusieurs jours", help_text="Lors de la validation la durée totale d'occupation (installation et rangement) sera bien indiqué sur plusieurs jours")
    manually_set_datetime = models.BooleanField(default=False, verbose_name="Définir manuellement les dates et horaires de début et de fin")

    starts_on = models.DateTimeField(verbose_name="Date et heure du début d'occupation", help_text="Calculée automatiquement sauf si la case précédente est cochée")
    ends_on = models.DateTimeField(verbose_name="Date et heure de fin d'occupation", help_text="Calculée automatiquement sauf si la case précédente est cochée")

    sent = models.BooleanField(default=False, verbose_name="Envoyé")
    sent_on = models.DateTimeField(editable=False, null=True, default=None, verbose_name="Envoyé le")

    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Créé le")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False, related_name="+")

    validated = models.BooleanField(default=False, verbose_name="L'événement est validé et apparait sur le planning étudiant")
    validated_on = models.DateTimeField(null=True, blank=True, verbose_name="Validé le", editable=False, )
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Validé par", editable=False, related_name="+")

    admin_display = models.BooleanField(default=False, verbose_name="L'événement apparait sur le planning de l'administration")
    member_display = models.BooleanField(default=True, verbose_name="L'événement apparait sur le planning des cotisants")

    rejected_for = SummernoteTextField(verbose_name="Raison du refus", null=True, blank=True)

    def get_datetime_display(self):
        start_time = self.starts_on.astimezone(timezone.get_current_timezone()).strftime('%Hh%M' if self.starts_on.minute != 0 else '%Hh')
        end_time = self.ends_on.astimezone(timezone.get_current_timezone()).strftime('%Hh%M' if self.ends_on.minute != 0 else '%Hh')
        if self.starts_on.date() == self.ends_on.date() or self.ends_on - self.starts_on <= timedelta(hours=10):
            return f"{self.starts_on.strftime('%d/%m/%Y')} - {start_time}/{end_time}"
        else:
            return f"{self.starts_on.strftime('%d/%m/%Y')} - {start_time} / {self.ends_on.strftime('%d/%m/%Y')} - {end_time}"

    def get_status_display(self):
        if self.validated:
            return mark_safe("<span class='badge badge-success'>Validée</span>")
        elif self.sent:
            return mark_safe("<span class='badge badge-info'>Envoyée</span>")
        elif self.rejected_for:
            return mark_safe("<span class='badge badge-warning'>Rejetée</span>")
        else:
            return mark_safe("<span class='badge badge-secondary'>A envoyer</span>")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Auto setup dates
        if not self.manually_set_datetime:
            self.starts_on = datetime.combine(self.start_date, self.start_time)
            if self.start_time >= self.end_time:
                self.ends_on = datetime.combine(self.start_date + timedelta(days=1), self.end_time)
            else:
                self.ends_on = datetime.combine(self.start_date, self.end_time)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        if self.event:
            return str(self.event)
        elif self.user:
            return str(self.user)
        else:
            return self.starts_on
