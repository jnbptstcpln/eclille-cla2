from datetime import datetime, timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone
from multiselectfield import MultiSelectField


class AbstractBlockedSlotManager(models.Manager):

    def for_admin(self):
        return self.filter(admin_display=True)

    def for_member(self):
        return self.filter(member_display=True)

    def is_range_free(self, start, end):
        if not self.filter(starts_on__lte=end, ends_on__gte=start, validated=True).count() == 0:
            return False
        events = self.filter(starts_on__lte=start, recurring=True).filter(Q(end_recurring__gte=end) | Q(end_recurring__isnull=True))
        for event in events:
            for d in event.recurring_days:
                if start.weekday() == d and end.weekday() == d:
                    if event.start_time <= end.time() and event.end_time >= start.time():
                        return False
                elif start.weekday() < d < end.weekday():
                    return False
                elif start.weekday() < d <= end.weekday():
                    if end.time() > event.start_time:
                        return False
                elif start.weekday() >= d and end.weekday() > d:
                    if start.time() < event.end_time:
                        return False

        return True


class AbstractBlockedSlot(models.Model):
    objects = AbstractBlockedSlotManager()

    class Meta:
        abstract = True
        ordering = "-created_on",

    class Days(models.IntegerChoices):
        MONDAY = 1, "Lundi"
        TUESDAY = 2, "Mardi"
        WEDNESDAY = 3, "Mercredi"
        THURSDAY = 4, "Jeudi"
        FRIDAY = 5, "Vendredi"
        SATURDAY = 6, "Samedi"
        SUNDAY = 0, "Dimanche"

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    name = models.CharField(max_length=50, default="RÉSERVÉ", verbose_name="Nom")
    start_date = models.DateField(verbose_name="Date", help_text="Sert aussi pour définir le début de la récurrence")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")
    recurring = models.BooleanField(default=False, verbose_name="Événement récurent")
    recurring_days = MultiSelectField(choices=Days.choices, blank=True, verbose_name="Jour(s) où ont lieu ce créneau selon la récurrence")
    end_recurring = models.DateField(verbose_name="Date de fin de la récurrence", null=True, blank=True)

    starts_on = models.DateTimeField(editable=False)
    ends_on = models.DateTimeField(editable=False)

    admin_display = models.BooleanField(default=False, verbose_name="Ce créneau apparait sur le planning de l'administration")
    member_display = models.BooleanField(default=True, verbose_name="Ce créneau apparait sur le planning des cotisants")

    def get_datetime_display(self):
        start_time = self.starts_on.astimezone(timezone.get_current_timezone()).strftime('%Hh%M' if self.starts_on.minute != 0 else '%Hh')
        end_time = self.ends_on.astimezone(timezone.get_current_timezone()).strftime('%Hh%M' if self.ends_on.minute != 0 else '%Hh')
        if self.starts_on.date() == self.ends_on.date() or self.ends_on - self.starts_on <= timedelta(hours=10):
            return f"{self.starts_on.strftime('%d/%m/%Y')} - {start_time}/{end_time}"
        else:
            return f"{self.starts_on.strftime('%d/%m/%Y')} - {start_time} / {self.ends_on.strftime('%d/%m/%Y')} - {end_time}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.starts_on = datetime.combine(self.start_date, self.start_time)
        if self.start_time >= self.end_time:
            self.ends_on = datetime.combine(self.start_date + timedelta(days=1), self.end_time)
        else:
            self.ends_on = datetime.combine(self.start_date, self.end_time)
        super().save(force_insert, force_update, using, update_fields)
