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


class SportActivity(models.Model):

    class Meta:
        verbose_name = "[SYNTHE] Sport ou activité"
        verbose_name_plural = "[SYNTHE] Sports ou activités"
        ordering = ("name",)

    name = models.CharField(max_length=50, verbose_name="Nom")
    description = models.CharField(
        max_length=255, blank=True, verbose_name="Description rapide"
    )
    available = models.BooleanField(
        default=True, verbose_name="Disponible à la sélection dans les réservations"
    )


class ReservationSyntheManager(models.Manager):

    def for_admin(self):
        return self.filter(
            validated=True, admin_display=True, event__cancelled_on__isnull=True
        )

    def for_member(self):
        return self.filter(
            validated=True, member_display=True, event__cancelled_on__isnull=True
        )

    def to_validate(self):
        return self.filter(
            validated=False, sent=True, event__cancelled_on__isnull=True
        ).order_by("sent_on")

    def is_range_free(self, start, end):
        return (
            self.filter(
                starts_on__lte=end,
                ends_on__gte=start,
                validated=True,
                event__cancelled_on__isnull=True,
            ).count()
            == 0
        )


class ReservationSynthe(models.Model):

    objects = ReservationSyntheManager()

    class Meta:
        ordering = ("-starts_on",)
        verbose_name = "[SYNTHE] Réservation"
        verbose_name_plural = "[SYNTHE] Réservations"

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="reservation_synthe",
        null=True,
        blank=True,
        verbose_name="Réserver dans le cadre de cet événement",
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Réserver à titre personnel par ce cotisant",
        editable=False,
    )

    description_event = SummernoteTextField(
        verbose_name="Description de l'événement",
        null=True,
        blank=True,
        help_text="Précisez ici comment va être organisé votre événement, quelles activités seront proposées et quels seront vos besoins (électrique, équipements particulier, ...)",
    )
    sport_activity = models.ForeignKey(
        SportActivity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Sport ou activité",
    )

    start_date = models.DateField(
        verbose_name="Date de début",
        help_text="Indiquez ici la date à partir de laquelle vous souhaitez occuper le lieu",
    )
    start_time = models.TimeField(
        verbose_name="Heure de début", help_text="Au format HH:MM (par exemple 18:30)"
    )
    end_time = models.TimeField(
        verbose_name="Heure de fin",
        help_text="Au format HH:MM (par exemple 01:00), elle correspond au moment où vous devez avoir rangé et nettoyé le lieu",
    )
    multiple_days = models.BooleanField(
        default=False,
        verbose_name="L'événement se déroule sur plusieurs jours",
        help_text="Lors de la validation la durée totale d'occupation (installation et rangement) sera bien indiqué sur plusieurs jours",
    )
    manually_set_datetime = models.BooleanField(
        default=False,
        verbose_name="Définir manuellement les dates et horaires de début et de fin",
    )

    starts_on = models.DateTimeField(
        verbose_name="Date et heure du début d'occupation",
        help_text="Calculée automatiquement sauf si la case précédente est cochée",
    )
    ends_on = models.DateTimeField(
        verbose_name="Date et heure de fin d'occupation",
        help_text="Calculée automatiquement sauf si la case précédente est cochée",
    )

    sent = models.BooleanField(default=False, verbose_name="Envoyé")
    sent_on = models.DateTimeField(
        editable=False, null=True, default=None, verbose_name="Envoyé le"
    )

    created_on = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="Créé le"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
    )

    validated = models.BooleanField(
        default=False,
        verbose_name="L'événement est validé et apparait sur le planning étudiant",
    )
    validated_on = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Validé le",
        editable=False,
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Validé par",
        editable=False,
        related_name="+",
    )

    admin_display = models.BooleanField(
        default=False,
        verbose_name="L'événement apparait sur le planning de l'administration",
    )
    member_display = models.BooleanField(
        default=True, verbose_name="L'événement apparait sur le planning des cotisants"
    )

    rejected_for = SummernoteTextField(
        verbose_name="Raison du refus", null=True, blank=True
    )

    def get_datetime_display(self):
        _starts_on = self.starts_on.astimezone(timezone.get_current_timezone())
        _ends_on = self.ends_on.astimezone(timezone.get_current_timezone())

        start_time = _starts_on.strftime("%Hh%M" if _starts_on.minute != 0 else "%Hh")
        end_time = _ends_on.astimezone(timezone.get_current_timezone()).strftime(
            "%Hh%M" if _ends_on.minute != 0 else "%Hh"
        )

        if _starts_on.date() == _ends_on.date() or _ends_on - _starts_on <= timedelta(
            hours=10
        ):
            return f"{_starts_on.strftime('%d/%m/%Y')} - {start_time}/{end_time}"
        else:
            return f"{_starts_on.strftime('%d/%m/%Y')} - {start_time} / {_ends_on.strftime('%d/%m/%Y')} - {end_time}"

    def get_status_display(self):
        if self.event.is_cancelled:
            return mark_safe("<span class='badge badge-danger'>Annulé</span>")
        elif self.validated:
            return mark_safe("<span class='badge badge-success'>Validée</span>")
        elif self.sent:
            return mark_safe("<span class='badge badge-info'>Envoyée</span>")
        elif self.rejected_for:
            return mark_safe("<span class='badge badge-warning'>Rejetée</span>")
        else:
            return mark_safe("<span class='badge badge-secondary'>A envoyer</span>")

    def send_notification(self):
        try:
            permission = Permission.objects.filter(
                content_type__app_label="cla_reservation",
                codename="change_reservationsynthe",
            ).first()
            groups = Group.objects.filter(permissions__in=[permission])
            for group in groups:
                try:
                    send_mail(
                        subject="[CLA][SYNTHÉ] Nouvelle demande de réservation",
                        from_email=settings.EMAIL_HOST_FROM,
                        recipient_list=[user.email for user in group.user_set.all()],
                        message="Une demande de réservation du synthé a été reçue",
                        html_message=render_to_string(
                            "cla_reservation/manage/mail.html",
                            {
                                "site_href": f"https://{settings.ALLOWED_HOSTS[0]}",
                                "detail_href": f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_reservation:manage:synthe-detail', self.pk)}",
                                "reservation": self,
                            },
                        ),
                    )
                except Exception as e:
                    print("synthé", e)
        except Exception as e:
            print("synthé", e)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # Auto setup dates
        if not self.manually_set_datetime:
            self.starts_on = datetime.combine(self.start_date, self.start_time)
            if self.start_time >= self.end_time:
                self.ends_on = datetime.combine(
                    self.start_date + timedelta(days=1), self.end_time
                )
            else:
                self.ends_on = datetime.combine(self.start_date, self.end_time)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        if self.event:
            return str(self.event)
        elif self.user:
            return str(self.user)
        else:
            return str(self.starts_on)


class BlockedSlotSynthe(AbstractBlockedSlot):

    class Meta:
        verbose_name = "[SYNTHE] Créneau bloqué"
        verbose_name_plural = "[SYNTHE] Créneaux bloqués"
