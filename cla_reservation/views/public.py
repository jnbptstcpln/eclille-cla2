import csv
from datetime import datetime

from django.db.models import Q
from django.views.generic import TemplateView
from django.contrib import admin, messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse, get_object_or_404, resolve_url
from django.http import HttpRequest, HttpResponseNotAllowed, Http404, HttpResponse, JsonResponse
from django.utils import timezone

from cla_association.models import Association

from cla_member.mixins import ClaMemberModuleMixin
from cla_reservation.mixins import PlanningMixin
from cla_reservation.models import ReservationBarbecue, ReservationFoyer, ReservationSynthe
from cla_reservation.models.barbecue import BlockedSlotBarbecue
from cla_reservation.models.foyer import BlockedSlotFoyer
from cla_reservation.models.synthe import BlockedSlotSynthe


class IndexView(ClaMemberModuleMixin, TemplateView):
    cla_member_active_section = "reservations"
    template_name = "cla_reservation/public/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'infrastructures': [
                {
                    'name': "Barbecue",
                    'icon': "fire",
                    'color': "red",
                    'to_review_count': ReservationBarbecue.objects.to_validate().count(),
                    'manage_permission': self.request.user.has_perm("cla_reservation.change_reservationbarbecue"),
                    'href': {
                        'manage': resolve_url("cla_reservation:manage:barbecue"),
                        'planning': resolve_url("cla_reservation:public:barbecue-planning"),
                        'reservation': resolve_url("cla_reservation:public:barbecue-reservation"),
                    }
                },
                {
                    'name': "Foyer",
                    'icon': "beer",
                    'color': "warning",
                    'to_review_count': ReservationFoyer.objects.to_validate().count(),
                    'manage_permission': self.request.user.has_perm("cla_reservation.change_reservationfoyer"),
                    'href': {
                        'manage': resolve_url("cla_reservation:manage:foyer"),
                        'planning': resolve_url("cla_reservation:public:foyer-planning"),
                        'reservation': resolve_url("cla_reservation:public:foyer-reservation"),
                    }
                }, {
                    'name': "Synthé",
                    'icon': "volleyball-ball",
                    'color': "green",
                    'to_review_count': ReservationSynthe.objects.to_validate().count(),
                    'manage_permission': self.request.user.has_perm("cla_reservation.change_reservationsynthe"),
                    'href': {
                        'manage': resolve_url("cla_reservation:manage:synthe"),
                        'planning': resolve_url("cla_reservation:public:synthe-planning"),
                        'reservation': resolve_url("cla_reservation:public:synthe-reservation"),
                    }

                }
            ]
        })
        return context


class AbstractPlanningView(PlanningMixin, ClaMemberModuleMixin, TemplateView):
    template_name = "cla_reservation/public/planning.html"
    cla_member_active_section = "reservations"
    config__reservation_clickable = False
    config__slot_clickable = False


class PlanningBarbecueView(AbstractPlanningView):
    planning_name = 'barbecue'
    model = ReservationBarbecue
    blocked_slot_model = BlockedSlotBarbecue


class ReservationBarbecueView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_reservation/public/reservation/barbecue/index.html"
    cla_member_active_section = "reservations"


class PlanningFoyerView(AbstractPlanningView):
    planning_name = 'foyer'
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer


class ReservationFoyerView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_reservation/public/reservation/foyer/index.html"
    cla_member_active_section = "reservations"


class PlanningSyntheView(AbstractPlanningView):
    planning_name = 'synthé'
    model = ReservationSynthe
    blocked_slot_model = BlockedSlotSynthe


class ReservationSyntheView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_reservation/public/reservation/synthe/index.html"
    cla_member_active_section = "reservations"
