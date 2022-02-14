from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, View
from icalendar import Event, Calendar

from cla_association.views.public import DetailView
from cla_reservation.mixins import PlanningSchoolAdminMixin
from cla_reservation.models import ReservationSynthe, ReservationFoyer, ReservationBarbecue, ReservationBibli, BlockedSlotBibli
from cla_reservation.models.barbecue import BlockedSlotBarbecue
from cla_reservation.models.foyer import BlockedSlotFoyer
from cla_reservation.models.synthe import BlockedSlotSynthe


class BarbecueView(PlanningSchoolAdminMixin, TemplateView):
    template_name = "cla_reservation/school_admin/planning.html"
    model = ReservationBarbecue
    blocked_slot_model = BlockedSlotBarbecue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'infrastructure_name': 'Barbecue'
        })
        return context


class BarbecueIcsView(PlanningSchoolAdminMixin, View):
    model = ReservationBarbecue
    blocked_slot_model = BlockedSlotBarbecue

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        cal = Calendar()
        for e in self.get_planning_items(timezone.now() - timedelta(days=15), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e['name'])
            event.add('dtstart', e['start'])
            event.add('dtend', e['end'])
            event.add('description', e['name'])
            event.add('location', e['place'])
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')


class BibliView(PlanningSchoolAdminMixin, TemplateView):
    template_name = "cla_reservation/school_admin/planning.html"
    model = ReservationBibli
    blocked_slot_model = BlockedSlotBibli

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'infrastructure_name': 'Bibli'
        })
        return context


class BibliIcsView(PlanningSchoolAdminMixin, View):
    model = ReservationBibli
    blocked_slot_model = BlockedSlotBibli

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        cal = Calendar()
        for e in self.get_planning_items(timezone.now() - timedelta(days=15), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e['name'])
            event.add('dtstart', e['start'])
            event.add('dtend', e['end'])
            event.add('description', e['name'])
            event.add('location', e['place'])
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')


class FoyerView(PlanningSchoolAdminMixin, TemplateView):
    template_name = "cla_reservation/school_admin/planning.html"
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'infrastructure_name': 'Foyer'
        })
        return context


class FoyerIcsView(PlanningSchoolAdminMixin, View):
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        cal = Calendar()
        for e in self.get_planning_items(timezone.now() - timedelta(days=15), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e['name'])
            event.add('dtstart', e['start'])
            event.add('dtend', e['end'])
            event.add('description', e['name'])
            event.add('location', e['place'])
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')


class SyntheView(PlanningSchoolAdminMixin, TemplateView):
    template_name = "cla_reservation/school_admin/planning.html"
    model = ReservationSynthe
    blocked_slot_model = BlockedSlotSynthe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'infrastructure_name': 'Barbecue'
        })
        return context


class SyntheIcsView(PlanningSchoolAdminMixin, View):
    model = ReservationSynthe
    blocked_slot_model = BlockedSlotSynthe

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        cal = Calendar()
        for e in self.get_planning_items(timezone.now() - timedelta(days=15), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e['name'])
            event.add('dtstart', e['start'])
            event.add('dtend', e['end'])
            event.add('description', e['name'])
            event.add('location', e['place'])
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')
