from django.views.generic import TemplateView

from cla_reservation.mixins import PlanningSchoolAdminMixin
from cla_reservation.models import ReservationSynthe, ReservationFoyer, ReservationBarbecue
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

