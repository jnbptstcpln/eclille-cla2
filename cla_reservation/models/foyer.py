import os
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_summernote.fields import SummernoteTextField

from cla_event.models import Event
from cla_reservation.models._base import AbstractBlockedSlot


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def beer_menu(cls, instance, filename):
        return cls._path(instance, ["cla_reservation", "foyer_beer_menu"], filename)

    @classmethod
    def rules(cls, instance, filename):
        return cls._path(instance, ["cla_reservation", "foyer_rules"], filename)


class BeerMenuManager(models.Manager):

    def last(self):
        return self.filter(available=True).order_by("-created_on").first()

    def is_range_free(self, start, end):
        return self.filter(starts_on__lte=end, ends_on__gte=start, validated=True).count() == 0


class BeerMenu(models.Model):

    objects = BeerMenuManager()

    class Meta:
        ordering = "-created_on",
        verbose_name = "[FOYER] Carte des bières"
        verbose_name_plural = "[FOYER] Cartes des bières"

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    file = models.FileField(upload_to=FilePath.beer_menu, blank=True, null=True, verbose_name="Fichier", help_text="De préférence au format PDF ou Excel")
    available = models.BooleanField(default=False, verbose_name="Cette version est disponible à la consultation")

    def __str__(self):
        return f"Carte des bières {self.created_on.strftime('%Y')}"


class RulesManager(models.Manager):

    def last(self):
        return self.filter(available=True).order_by("-created_on").first()


class FoyerRules(models.Model):
    objects = RulesManager()

    class Meta:
        ordering = "-created_on",
        verbose_name = "[FOYER] Charte du foyer"
        verbose_name_plural = "[FOYER] Chartes du foyer"

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    description = SummernoteTextField(verbose_name="Présentation", help_text="Rappelle des éléments important tel que les différents chèques de cautions")
    file = models.FileField(upload_to=FilePath.rules, blank=True, null=True, verbose_name="Fichier", help_text="De préférence au format PDF ou Excel")
    available = models.BooleanField(default=False, verbose_name="Cette version est disponible à la consultation")

    def __str__(self):
        return f"Charte {self.created_on.strftime('%Y')}"


class FoyerItem(models.Model):

    class Meta:
        verbose_name = "[FOYER] Équipement supplémentaire"
        verbose_name_plural = "[FOYER] Équipements supplémentaires"
        ordering = "name",

    name = models.CharField(max_length=50, verbose_name="Nom")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description rapide")
    available = models.BooleanField(default=True, verbose_name="Disponible à la sélection dans les réservations")
    deposit = models.PositiveIntegerField(null=True, blank=True, default=None, help_text="Laisser vide si pas de caution pour cet équipement")

    def __str__(self):
        return self.name


class ReservationFoyerManager(models.Manager):

    def for_admin(self):
        return self.filter(validated=True, admin_display=True)

    def for_member(self):
        return self.filter(validated=True, member_display=True)

    def to_validate(self):
        return self.filter(validated=False, sent=True).order_by('sent_on')

    def is_range_free(self, start, end):
        return self.filter(starts_on__lte=end, ends_on__gte=start, validated=True).count() == 0


class ReservationFoyer(models.Model):

    objects = ReservationFoyerManager()

    class Meta:
        verbose_name = "[FOYER] Réservation"
        verbose_name_plural = "[FOYER] Réservation"
        ordering = "-starts_on",

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="reservation_foyer", null=True, blank=True, verbose_name="Réserver dans le cadre de cet événement", editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="+", null=True, blank=True, verbose_name="Réserver à titre personnel par ce cotisant", editable=False)

    description = SummernoteTextField(verbose_name="Description de l'événement", help_text="Précisez ici comment va être organisé votre événement, quelles activités seront proposées et quels seront vos besoins (électrique, équipements particulier, ...)")

    beer_selection = models.TextField(max_length=500, blank=True, verbose_name="Sélection des fûts", help_text="Indiquez sur chaque ligne \"Bière : Nombre de fûts\"")
    items = models.ManyToManyField(FoyerItem, verbose_name="Équipements supplémentaires", blank=True)

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
        _starts_on = self.starts_on.astimezone(timezone.get_current_timezone())
        _ends_on = self.ends_on.astimezone(timezone.get_current_timezone())

        start_time = _starts_on.strftime('%Hh%M' if _starts_on.minute != 0 else '%Hh')
        end_time = _ends_on.astimezone(timezone.get_current_timezone()).strftime('%Hh%M' if _ends_on.minute != 0 else '%Hh')

        if _starts_on.date() == _ends_on.date() or _ends_on - _starts_on <= timedelta(hours=10):
            return f"{_starts_on.strftime('%d/%m/%Y')} - {start_time}/{end_time}"
        else:
            return f"{_starts_on.strftime('%d/%m/%Y')} - {start_time} / {_ends_on.strftime('%d/%m/%Y')} - {end_time}"

    def get_status_display(self):
        if self.validated:
            return mark_safe("<span class='badge badge-success'>Validée</span>")
        elif self.sent:
            return mark_safe("<span class='badge badge-info'>Envoyée</span>")
        elif self.rejected_for:
            return mark_safe("<span class='badge badge-warning'>Rejetée</span>")
        else:
            return mark_safe("<span class='badge badge-secondary'>A envoyer</span>")

    def send_notification(self):
        try:
            permission = Permission.objects.filter(content_type__app_label='cla_reservation', codename='change_reservationfoyer').first()
            groups = Group.objects.filter(permissions__in=[permission])
            for group in groups:
                try:
                    send_mail(
                        subject='[CLA][FOYER] Nouvelle demande de réservation',
                        from_email=settings.EMAIL_HOST_FROM,
                        recipient_list=[user.email for user in group.user_set.all()],
                        message="Une demande de réservation du foyer a été reçue",
                        html_message=render_to_string(
                            'cla_reservation/manage/mail.html',
                            {
                                'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                                'detail_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_reservation:manage:foyer-detail', self.pk)}",
                                'reservation': self
                            }
                        ),
                    )
                except Exception as e:
                    print("foyer", e)
        except Exception as e:
            print("foyer", e)


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


class BlockedSlotFoyer(AbstractBlockedSlot):

    class Meta:
        verbose_name = "[FOYER] Créneau bloqué"
        verbose_name_plural = "[FOYER] Créneaux bloqués"
