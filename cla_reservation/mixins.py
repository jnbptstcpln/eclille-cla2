from datetime import timedelta, date, datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, resolve_url

from cla_event.mixins import EventAssociationMixin
from cla_event.models import Event
from cla_member.mixins import ClaMemberModuleMixin
from cla_reservation.models import ReservationFoyer, ReservationBarbecue, ReservationSynthe


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
        return {
            'start_date': self.event.start_date,
            'start_time': (datetime.combine(date.today(), self.event.start_time) - timedelta(hours=1, minutes=30)).time(),
            'end_time': (datetime.combine(date.today(), self.event.end_time) + timedelta(hours=1)).time(),
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


class ReservationManageMixin(ClaMemberModuleMixin):
    cla_member_active_section = "reservations"

    def dispatch(self, request, *args, **kwargs):
        if not self.has_any_reservation_permission():
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class AbstractReservationItemManageMixin(ClaMemberModuleMixin):
    cla_member_active_section = "reservations"
    cla_reservation_active_section = "index"
    model = None
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
                'id': "planning",
                'label': "Planning",
                'href': resolve_url(f"cla_reservation:manage:{self.namespace}")
            },
            {
                'id': "beers",
                'label': "Bières",
                'href': resolve_url(f"cla_reservation:manage:{self.namespace}")
            }
        ]
        return sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_active': 'cla_member',
            'sections_navigation': self.get_sections_navigation(),
            'section_active': self.cla_reservation_active_section,
            'to_review': self.model.objects.to_validate(),
            'is_range_free': self.model.objects.is_range_free(self.object.starts_on, self.object.ends_on) if hasattr(self, 'object') else None,
            'event_is_range_free': Event.objects.is_range_free(self.object.event.starts_on, self.object.event.ends_on) if hasattr(self, 'object') else None,
            'reservation_item': self.get_reservation_item()
        })
        return context


class ReservationBarbecueManageMixin(AbstractReservationItemManageMixin):
    model = ReservationBarbecue
    permission_name = "cla_reservation.change_reservationbarbecue"
    namespace = "barbecue"

    def get_reservation_item(self):
        return {
            'name': "Barbecue",
            'icon': "fire",
            'color': "red",
        }


class ReservationFoyerManageMixin(AbstractReservationItemManageMixin):
    model = ReservationFoyer
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
    permission_name = "cla_reservation.change_reservationsynthe"
    namespace = "synthe"

    def get_reservation_item(self):
        return {
            'name': "Synthé",
            'icon': "volleyball-ball",
            'color': "green",
        }
