from datetime import timedelta, date, datetime

import bleach
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render, resolve_url
from django.utils import timezone

from cla_event.mixins import EventAssociationMixin
from cla_event.models import Event
from cla_member.mixins import ClaMemberModuleMixin
from cla_reservation.models import ReservationFoyer, ReservationBarbecue, ReservationSynthe, ReservationDanceHall
from cla_reservation.models.barbecue import BlockedSlotBarbecue
from cla_reservation.models.bibli import ReservationBibli, BlockedSlotBibli
from cla_reservation.models.dancehall import BlockedSlotDanceHall
from cla_reservation.models.foyer import BlockedSlotFoyer
from cla_reservation.models.synthe import BlockedSlotSynthe


class ReservationAssociationMixin(EventAssociationMixin):
    creating = False
    reservation = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.reservation = self.get_reservation()
        if self.reservation is None:
            self.creating = True
            self.reservation = self.model(**self.get_reservation_kwargs())

    def dispatch(self, request, *args, **kwargs):
        # If the event was sent or validated directly display a read only view
        # or redirect if no reservation was associated with the event
        if self.event.sent or self.event.validated:
            if self.creating:
                return redirect("cla_event:association:update", self.association.slug, self.event.pk)
            else:
                return render(self.request, self.template_name, self.get_context_data())
        return super().dispatch(request, *args, **kwargs)

    def get_reservation(self):
        return None

    def get_reservation_kwargs(self):
        start_time = self.event.start_time
        end_time = self.event.end_time
        if self.event.public:
            start_time = (datetime.combine(date.today(), self.event.start_time) - timedelta(hours=1, minutes=30)).time()
            end_time = (datetime.combine(date.today(), self.event.end_time) + timedelta(hours=1)).time()
        return {
            'start_date': self.event.start_date,
            'start_time': start_time,
            'end_time': end_time,
            'multiple_days': self.event.multiple_days
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.reservation})
        return kwargs

    def form_valid(self, form):
        success_message = "Les changements ont bien été enregistrée"
        if self.creating:
            form.instance.created_by = self.request.user
            form.instance.event = self.event
            success_message = "La réservation a bien été créée"

        self.reservation = form.save()

        response = super().form_valid(form)
        messages.success(self.request, success_message)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'reservation': self.reservation
        })
        return context


class AbstractReservationItemManageMixin(ClaMemberModuleMixin):
    cla_member_active_section = "reservations"
    cla_reservation_active_section = "index"
    model = None
    blocked_slot_model = None
    permission_name = None
    namespace = None

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm(self.permission_name):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_reservation_item(self):
        return {
            'name': "__RESERVATION_NAME__",
            'icon': "__RESERVATION_ICON__",
            'color': "__RESERVATION_COLOR__",
        }

    def get_sections_navigation(self):
        sections = [
            {
                'id': "index",
                'label': "Réservations",
                'href': resolve_url(f"cla_reservation:manage:{self.namespace}")
            },
            {
                'id': "blockedslot",
                'label': "Créneaux bloqués",
                'href': resolve_url(f"cla_reservation:manage:{self.namespace}-blockedslot-list")
            },
            {
                'id': "planning",
                'label': "Planning",
                'href': resolve_url(f"cla_reservation:manage:{self.namespace}-planning")
            }
        ]
        return sections

    def is_range_free(self):
        if hasattr(self, 'object'):
            _starts_on = self.object.starts_on.astimezone(timezone.get_current_timezone())
            _ends_on = self.object.ends_on.astimezone(timezone.get_current_timezone())
            return self.model.objects.is_range_free(self.object.starts_on, self.object.ends_on) \
                   and self.blocked_slot_model.objects.is_range_free(_starts_on, _ends_on)  # Need to perform the operation with naive timezone datetime
        return None

    def is_event_range_free(self):
        if hasattr(self, 'object') and hasattr(self.object, 'event'):
            return Event.objects.is_range_free(self.object.event.starts_on, self.object.event.ends_on)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_active': 'cla_member',
            'sections_navigation': self.get_sections_navigation(),
            'section_active': self.cla_reservation_active_section,
            'to_review': self.model.objects.to_validate() if hasattr(self.model.objects, 'to_validate') else None,
            'is_range_free': self.is_range_free() if hasattr(self.model.objects, 'to_validate') else None,
            'event_is_range_free': self.is_event_range_free(),
            'reservation_item': self.get_reservation_item()
        })
        return context


class ReservationBarbecueManageMixin(AbstractReservationItemManageMixin):
    model = ReservationBarbecue
    blocked_slot_model = BlockedSlotBarbecue
    permission_name = "cla_reservation.change_reservationbarbecue"
    namespace = "barbecue"

    def get_reservation_item(self):
        return {
            'name': "Barbecue",
            'icon': "fire",
            'color': "red",
        }


class ReservationBibliManageMixin(AbstractReservationItemManageMixin):
    model = ReservationBibli
    blocked_slot_model = BlockedSlotBibli
    permission_name = "cla_reservation.change_reservationbibli"
    namespace = "bibli"

    def get_reservation_item(self):
        return {
            'name': "Bibli",
            'icon': "books",
            'color': "blue",
        }


class ReservationFoyerManageMixin(AbstractReservationItemManageMixin):
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer
    permission_name = "cla_reservation.change_reservationfoyer"
    namespace = "foyer"

    def get_reservation_item(self):
        return {
            'name': "Foyer",
            'icon': "beer",
            'color': "warning",
        }


class ReservationSyntheManageMixin(AbstractReservationItemManageMixin):
    model = ReservationSynthe
    blocked_slot_model = BlockedSlotSynthe
    permission_name = "cla_reservation.change_reservationsynthe"
    namespace = "synthe"

    def get_reservation_item(self):
        return {
            'name': "Synthé",
            'icon': "volleyball-ball",
            'color': "green",
        }


class ReservationDanceHallManageMixin(AbstractReservationItemManageMixin):
    model = ReservationDanceHall
    blocked_slot_model = BlockedSlotDanceHall
    permission_name = "cla_reservation.change_reservationdancehall"
    namespace = "dancehall"

    def get_reservation_item(self):
        return {
            'name': "Salle de danse",
            'icon': "house",
            'color': "pink",
        }


class PlanningMixin:
    planning_name = '__PLANNING_NAME__'
    model = None
    blocked_slot_model = None

    config__reservation_clickable = True
    config__slot_clickable = True
    config__reservation_content = False
    config__reservation_popover = False
    config__reservation_non_public_attrs = {
        'backgroundColor': '#aaa',
        'textColor': '#222',
        'borderColor': '#222'
    }
    config__reservation_non_validated_attrs = {
        'backgroundColor': '#eee',
        'textColor': '#888',
        'borderColor': '#888',
    }
    config__reservation_cancelled_attrs = {
        'backgroundColor': '#fee',
        'textColor': '#f88',
        'borderColor': '#f88',
    }

    def get_reservation_content(self, instance):
        return {
            'html': f"[{instance.association.name}]<br>{instance.name}"
        }

    def get_reservation_class_names(self, instance):
        class_names = []
        if not instance.validated:
            class_names.append('border-dash')
        return class_names

    def get_reservation_url(self, instance):
        return None

    def get_slot_url(self, instance):
        return None

    def get_reservation_title(self, instance):
        if hasattr(instance, 'event') and instance.event and instance.event.public:
            if instance.event.is_cancelled:
                return f"[ANNULÉ] {instance.event.association.name}"
            return instance.event.association.name
        else:
            return f"Réservé"

    def get_reservation_popover(self, instance: Event):
        return {
            'popover': True,
            'popover_content': bleach.clean(
                (
                    f"""
                    <div class='text-center min-width-100'>
                        <div class='font-weight-bold text-lg'>{instance.event.association.name}</div>
                        <div>{"[ANNULÉ] " if instance.event.is_cancelled else ""}{instance.event.name}</div>
                    </div>
                    """
                ) if instance.event else (
                    f"""
                    <div class='text-center min-width-100'>
                        <div class='font-weight-bold' style='text-lg'>{instance.user.first_name} {instance.user.last_name}</div>
                    </div>
                    """
                )
                ,
                tags=['span', 'br', 'div'],
                attributes={'span': ['class'], 'div': ['class']}
            ),
        }

    def build_reservation(self, instance):
        r = {
            'title': self.get_reservation_title(instance),
            'classNames': self.get_reservation_class_names(instance),
            'start': instance.starts_on.astimezone(timezone.get_current_timezone()),
            'end': instance.ends_on.astimezone(timezone.get_current_timezone()),
        }

        if self.config__reservation_clickable:
            r['url'] = self.get_reservation_url(instance)
        if instance.event and not instance.event.public and self.config__reservation_non_public_attrs:
            r.update(self.config__reservation_non_public_attrs)
        if not instance.validated:
            r.update(self.config__reservation_non_validated_attrs)
        if hasattr(instance, 'event') and instance.event and instance.event.is_cancelled:
            r.update(self.config__reservation_cancelled_attrs)
        if self.config__reservation_content:
            r.update({'reservationContent': self.get_reservation_content(instance)})
        if self.config__reservation_popover:
            r.update(self.get_reservation_popover(instance))
        return r

    def build_slot(self, instance, recurring=False):

        title = instance.name
        if hasattr(instance, 'event') and instance.event and instance.event.is_cancelled:
            title = f"[ANNULE] {title}"
        print(title)

        s = {
            'title': title,
            'backgroundColor': '#eee',
            'textColor': '#555',
        }

        if hasattr(instance, 'event') and instance.event and instance.event.is_cancelled:
            s['backgroundColor'] = '#fee'
            s['textColor'] = '#f55'

        if recurring:
            s.update({
                'daysOfWeek': instance.recurring_days,
                'startTime': instance.start_time,
                'endTime': instance.end_time,
                'startRecur': instance.start_date.isoformat(),
                'endRecur': instance.end_recurring.isoformat() if instance.end_recurring else None,
            })
        else:
            s.update({
                'start': instance.starts_on.astimezone(timezone.get_current_timezone()),
                'end': instance.ends_on.astimezone(timezone.get_current_timezone()),
            })

        if self.config__slot_clickable:
            s['url'] = self.get_slot_url(instance)

        return s

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.for_member()

    def get_reservation_base_queryset(self):
        return self.model.objects.for_member()

    def get_recurring_reservations(self, start, end):
        slots = self.get_blocked_slot_base_queryset().filter(recurring=True, start_date__lte=end.date()).filter(Q(end_recurring__gte=start.date()) | Q(end_recurring__isnull=True))
        return [
            self.build_slot(s, recurring=True) for s in slots
        ]

    def get_fixed_reservations(self, start, end):
        slots = self.get_blocked_slot_base_queryset().filter(starts_on__gte=start, ends_on__lte=end, recurring=False)
        return [
            self.build_slot(s) for s in slots
        ]

    def get_reservations(self, start, end):
        reservations = self.get_reservation_base_queryset().filter(starts_on__gte=start, ends_on__lte=end)
        return [
            self.build_reservation(r) for r in reservations
        ]

    def get_planning_items(self, start, end):
        return self.get_reservations(start, end) + self.get_fixed_reservations(start, end) + self.get_recurring_reservations(start, end)

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('format') == "json":
            start = datetime.strptime(self.request.GET.get('start'), "%Y-%m-%dT%H:%M:%S")
            end = datetime.strptime(self.request.GET.get('end'), "%Y-%m-%dT%H:%M:%S")
            return JsonResponse(self.get_planning_items(start, end), safe=False)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'name': self.planning_name
        })
        return context


class PlanningAdminMixin(PlanningMixin):

    def get_reservation_title(self, instance):
        if hasattr(instance, 'event') and instance.event and instance.event.public:
            if instance.event.is_cancelled:
                return f"[ANNULÉ] {instance.event.association.name}"
            return instance.event.association.name
        else:
            return f"Cotisant"


class PlanningSchoolAdminMixin(PlanningMixin):

    TOKEN_BARBECUE = "S3qyQLouijRL13xGN2eF"
    TOKEN_BIBLI = "wZcEFvqN3NxE5QVCPnP9"
    TOKEN_FOYER = "2zlSMSyL35I6dfjQ8P0u"
    TOKEN_SYNTHE = "FSh8ssZ3deZ4Nr3bfRlK"
    TOKEN_DANCEHALL = "Wu1GCPjkmLqMoJvTi7YY"

    config__reservation_clickable = False
    config__slot_clickable = False
    config__reservation_popover = True

    def get_reservation_base_queryset(self):
        return self.model.objects.for_admin()

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.for_admin()

    def build_reservation(self, instance):
        reservation = super().build_reservation(instance)
        reservation.update({
            'start': instance.event.starts_on.astimezone(timezone.get_current_timezone()),
            'end': instance.event.ends_on.astimezone(timezone.get_current_timezone())
        })
        return reservation

    def get_reservation_title(self, instance):
        if hasattr(instance, 'event') and instance.event:
            if instance.event.is_cancelled:
                return f"[ANNULÉ] {instance.event.association.name}"
            return instance.event.association.name
        else:
            return f"Cotisant"

    def get_reservation_popover(self, instance: Event):

        try:
            phone = instance.created_by.infos.phone
        except:
            phone = "Non spécifié"

        return {
            'popover': True,
            'popover_content': bleach.clean(
                (
                    f"""
                    <div class='text-center min-width-100'>
                        <div class='font-weight-bold text-lg'>{instance.event.association.name}</div>
                        <div class='font-weight-bold text-lg'>{instance.event.type.name}</div>
                        <div>{"[ANNULÉ] " if instance.event.is_cancelled else ""}{instance.event.name}</div>
                        <hr>
                        <div>{instance.created_by.first_name} {instance.created_by.last_name}</div>
                        <div class='text-sm'>Tel : {phone}</div>
                    </div>
                    """
                ) if instance.event else (
                    f"""
                    <div class='text-center min-width-100'>
                        <div class='font-weight-bold' style='text-lg'>{instance.user.first_name} {instance.user.last_name}</div>
                        <div class='text-sm'>Tel : {phone}</div>
                    </div>
                    """
                )
                ,
                tags=['span', 'br', 'div', 'hr'],
                attributes={'span': ['class'], 'div': ['class']}
            ),
        }
