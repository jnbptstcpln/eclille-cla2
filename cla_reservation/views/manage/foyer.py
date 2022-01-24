from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from icalendar import Calendar, Event

from cla_auth.mixins import JWTMixin
from cla_reservation.forms.foyer import ReservationFoyerAdminForm, ReservationFoyerValidateForm, ReservationFoyerRejectForm, BlockedSlotFoyerForm
from cla_reservation.mixins import ReservationFoyerManageMixin, PlanningAdminMixin
from cla_reservation.models import ReservationFoyer
from cla_reservation.models.foyer import BlockedSlotFoyer
from cla_reservation.views._blockedslot import AbstractBlockedSlotListView, AbstractBlockedSlotCreateView, AbstractBlockedSlotUpdateView, AbstractBlockedSlotDeleteView


class FoyerListView(ReservationFoyerManageMixin, ListView):
    template_name = "cla_reservation/manage/foyer/list.html"
    model = ReservationFoyer
    queryset = ReservationFoyer.objects.filter(validated=True, sent=True)
    paginate_by = 20


class FoyerPlanningView(PlanningAdminMixin, ReservationFoyerManageMixin, TemplateView):
    cla_reservation_active_section = "planning"
    template_name = "cla_reservation/manage/planning.html"
    planning_name = 'foyer'
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer

    def get_reservation_url(self, instance):
        return resolve_url("cla_reservation:manage:foyer-detail", instance.pk)

    def get_slot_url(self, instance):
        return resolve_url("cla_reservation:manage:foyer-blockedslot-update", instance.pk)

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'school_admin_planning_href': resolve_url('cla_reservation:school_admin:foyer'),
            'sync_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_reservation:manage:foyer-export')}?token={FoyerIcsFileView.generate_token()}"
        })
        return context


class FoyerDetailView(PlanningAdminMixin, ReservationFoyerManageMixin, DetailView):
    template_name = "cla_reservation/manage/foyer/details.html"
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer

    config__reservation_clickable = False
    config__slot_clickable = False
    config__reservation_popover = True

    def build_reservation(self, instance):
        r = super().build_reservation(instance)
        if instance.pk == self.get_object().pk:
            r['borderColor'] = "red"
        return r

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.all()


class FoyerUpdateView(ReservationFoyerManageMixin, UpdateView):
    template_name = "cla_reservation/manage/foyer/update.html"
    form_class = ReservationFoyerAdminForm
    model = ReservationFoyer

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:foyer-update", self.object.pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrée")
        return response


class FoyerValidateView(ReservationFoyerManageMixin, UpdateView):
    template_name = "cla_reservation/manage/foyer/validate.html"
    form_class = ReservationFoyerValidateForm
    model = ReservationFoyer

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:foyer")

    def form_valid(self, form):
        form.instance.validated_by = self.request.user
        response = super().form_valid(form)
        form.instance.event.check_validation(self.request.user)
        messages.success(self.request, "La réservation a bien été validée")
        return response


class FoyerRejectView(ReservationFoyerManageMixin, UpdateView):
    template_name = "cla_reservation/manage/foyer/reject.html"
    form_class = ReservationFoyerRejectForm
    model = ReservationFoyer

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:foyer")

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.event.reject("Votre réservation du foyer a été rejeté")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response


class FoyerBlockedSlotListView(ReservationFoyerManageMixin, AbstractBlockedSlotListView):
    infrastructure_name = "foyer"
    infrastructure_id = "foyer"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotFoyer


class FoyerBlockedSlotCreateView(ReservationFoyerManageMixin, AbstractBlockedSlotCreateView):
    infrastructure_name = "foyer"
    infrastructure_id = "foyer"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotFoyer
    form_class = BlockedSlotFoyerForm


class FoyerBlockedSlotUpdateView(ReservationFoyerManageMixin, AbstractBlockedSlotUpdateView):
    infrastructure_name = "foyer"
    infrastructure_id = "foyer"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotFoyer
    form_class = BlockedSlotFoyerForm


class FoyerBlockedSlotDeleteView(ReservationFoyerManageMixin, AbstractBlockedSlotDeleteView):
    infrastructure_name = "foyer"
    infrastructure_id = "foyer"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotFoyer


class FoyerIcsFileView(PlanningAdminMixin, JWTMixin, View):
    jwt_payload_key = "cla_reservation:manage:foyer"
    model = ReservationFoyer
    blocked_slot_model = BlockedSlotFoyer

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        for e in self.get_planning_items(timezone.now(), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e.get('title'))
            event.add('dtstart', e.get('start'))
            event.add('dtend', e.get('end'))
            event.add('description', e.get('name'))
            event.add('location', e.get('Barbecue'))
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')
