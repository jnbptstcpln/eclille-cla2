import os
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import resolve_url
from django_resized import ResizedImageField
from django_summernote.fields import SummernoteTextField

from cla_association.models import Association
from cla_auth.models import UserInfos, Service


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s-%s.%s" % (uuid.uuid4(), instance.slug, ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def event_poster(cls, instance, filename):
        return cls._path(instance, ["cla_event", "event_poster"], filename)


class EventType(models.Model):
    class Meta:
        verbose_name = "Type"
        verbose_name_plural = "Types"

    name = models.CharField(max_length=50, verbose_name="Nom")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")
    available = models.BooleanField(default=True, verbose_name="Disponible au choix", help_text="Permet de restreindre l'accès de ce type d'événement aux seuls administrateurs")

    def __str__(self):
        return self.name


class EventPlace(models.Model):
    class Meta:
        verbose_name = "Lieu"
        verbose_name_plural = "Lieux"

    name = models.CharField(max_length=50, verbose_name="Nom")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")
    available = models.BooleanField(default=True, verbose_name="Disponible au choix", help_text="Permet de restreindre l'accès de ce type d'événement aux seuls administrateurs")

    def __str__(self):
        return self.name


class EventManager(models.Manager):
    pass


class Event(models.Model):
    objects = EventManager()

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = "-starts_on",

    association = models.ForeignKey(Association, on_delete=models.PROTECT, verbose_name="Association organisatrice", related_name="events")
    name = models.CharField(max_length=100, verbose_name="Nom")
    name_school = models.CharField(max_length=100, verbose_name="Nom \"admin compatible\"")
    type = models.ForeignKey(EventType, on_delete=models.PROTECT, verbose_name="Type", related_name="events")
    place = models.ForeignKey(EventPlace, on_delete=models.PROTECT, verbose_name="Lieu", related_name="events")
    presentation_html = SummernoteTextField(verbose_name="Présentation de l'événement", blank=True)
    start_date = models.DateField(verbose_name="Date")
    start_time = models.TimeField(verbose_name="Heure de début", help_text="Au format HH:MM (par exemple 20:00)")
    end_time = models.TimeField(verbose_name="Heure de fin", help_text="Au format HH:MM (par exemple 00:00), si l'heure de fin est inférieure à l'heure de début, cette dernière sera considérée comme étant le lendemain")
    multiple_days = models.BooleanField(default=False, verbose_name="L'événement se déroule sur plusieurs jours", help_text="Lors de la validation l'événement sera bien indiqué sur plusieurs jours")
    manually_set_datetime = models.BooleanField(default=False, verbose_name="Définir manuellement les dates et horaires de début et de fin")
    starts_on = models.DateTimeField(verbose_name="Date et heure de début", help_text="Calculée automatiquement sauf si la case précédente est cochée")
    ends_on = models.DateTimeField(verbose_name="Date et heure de fin", help_text="Calculée automatiquement sauf si la case précédente est cochée")
    poster = ResizedImageField(size=[827, 1170], force_format="PNG", upload_to=FilePath.event_poster, null=True, blank=True, verbose_name="Affiche de l'événement", help_text="Au format A4 (827px*1170px)")

    sent = models.BooleanField(default=False, verbose_name="Envoyé")
    sent_on = models.DateTimeField(editable=False, null=True, default=None, verbose_name="Envoyé le")

    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Créé le")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False, related_name="+")

    validated = models.BooleanField(default=False, verbose_name="L'événement est validé et apparait sur le planning étudiant")
    validated_on = models.DateTimeField(null=True, blank=True, verbose_name="Validé le", editable=False, )
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Validé par", editable=False, related_name="+")

    admin_display = models.BooleanField(default=False, verbose_name="L'événement apparait sur le planning envoyé à l'administration")

    def get_reservation_barbecue(self):
        if (hasattr(self, 'reservation_barbecue')):
            return self.reservation_barbecue
        return None

    def get_reservation_foyer(self):
        if (hasattr(self, 'reservation_foyer')):
            return self.reservation_foyer
        return None

    def get_reservation_synthe(self):
        if (hasattr(self, 'reservation_synthe')):
            return self.reservation_synthe
        return None



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
        return f"[{self.association.name}] {self.name}"
