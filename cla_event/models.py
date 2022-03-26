import os
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import resolve_url
from django.template.defaultfilters import date
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_resized import ResizedImageField
from django_summernote.fields import SummernoteTextField

from cla_association.models import Association
from cla_auth.models import UserInfos, Service


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s-%s.%s" % (uuid.uuid4(), instance.id, ext)
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

    def is_range_free(self, start, end):
        return self.filter(starts_on__lte=end, ends_on__gte=start, validated=True, public=True).count() == 0

    def for_admin(self):
        return self.filter(validated=True, admin_display=True, public=True)

    def for_member(self):
        return self.filter(validated=True, member_display=True, public=True)


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

    public = models.BooleanField(default=True, verbose_name="Événement public à faire apparaitre sur le planning",
                                 help_text="Décocher cette case si cet événement correspond aux activités internes de votre association (par exemple une réunion pour laquelle vous souhaitez réserver un local)")

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

    def get_reservation_barbecue(self):
        if (hasattr(self, 'reservation_barbecue')):
            return self.reservation_barbecue
        return None

    def get_reservation_bibli(self):
        if (hasattr(self, 'reservation_bibli')):
            return self.reservation_bibli
        return None

    def get_reservation_foyer(self):
        if (hasattr(self, 'reservation_foyer')):
            return self.reservation_foyer
        return None

    def get_reservation_synthe(self):
        if (hasattr(self, 'reservation_synthe')):
            return self.reservation_synthe
        return None

    def get_reservation_dancehall(self):
        if (hasattr(self, 'reservation_dancehall')):
            return self.reservation_dancehall
        return None

    @property
    def reservations(self):
        return {
            'barbecue': self.get_reservation_barbecue(),
            'bibli': self.get_reservation_bibli(),
            'foyer': self.get_reservation_foyer(),
            'synthe': self.get_reservation_synthe(),
            'dancehall': self.get_reservation_dancehall(),
        }

    def reject(self, rejected_for):
        self.sent = False
        self.rejected_for = rejected_for
        self.save()
        for name, reservation in self.reservations.items():
            if reservation:
                reservation.sent = False
                reservation.validated = False
                reservation.save()

    def check_validation(self, user):
        if self.are_reservations_validated():
            # If the event is not public (it doesn't appear on planning) then
            # we can automatically validated the event when all associated reservations
            # are validated
            if not self.public:
                self.validated = True
                self.validated_by = user
                self.validated_on = timezone.now()
                self.save()
            else:
                # All reservation are validated meaning the event can be validated,
                # sending a notification to ask for the event validation
                self.send_notification()

    def are_reservations_validated(self):
        reservations = [r for _, r in self.reservations.items() if r is not None]
        if len(reservations) > 0:
            return all([r.validated for r in reservations])
        return True

    def send_notification(self):
        try:
            permission = Permission.objects.filter(content_type__app_label='cla_event', codename='change_event').first()
            groups = Group.objects.filter(permissions__in=[permission])
            for group in groups:
                try:
                    send_mail(
                        subject='[CLA] Nouvel événement à valider',
                        from_email=settings.EMAIL_HOST_FROM,
                        recipient_list=[user.email for user in group.user_set.all()],
                        message="Une demande de validation d'événement a été reçu",
                        html_message=render_to_string(
                            'cla_event/manage/mail.html',
                            {
                                'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                                'detail_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_event:manage:detail', self.pk)}",
                                'event': self
                            }
                        ),
                    )
                except Exception as e:
                    print("event", e)
        except Exception as e:
            print("event", e)

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
