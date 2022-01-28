from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from icalendar import Event, Calendar

from cla_auth.mixins import JWTMixin
from cla_reservation.forms.bibli import ReservationBibliAssociationAdminForm, ReservationBibliValidateForm, ReservationBibliRejectForm, ReservationBibliMemberAdminForm, BlockedSlotBibliForm
from cla_reservation.mixins import ReservationBibliManageMixin, PlanningAdminMixin
from cla_reservation.models import ReservationBibli
from cla_reservation.models.bibli import BlockedSlotBibli
from cla_reservation.views._blockedslot import AbstractBlockedSlotListView, AbstractBlockedSlotCreateView, AbstractBlockedSlotUpdateView, AbstractBlockedSlotDeleteView


class BibliListView(ReservationBibliManageMixin, ListView):
    template_name = "cla_reservation/manage/bibli/list.html"
    model = ReservationBibli
    queryset = ReservationBibli.objects.filter(validated=True, sent=True)
    paginate_by = 20


class BibliPlanningView(PlanningAdminMixin, ReservationBibliManageMixin, TemplateView):
    cla_reservation_active_section = "planning"
    template_name = "cla_reservation/manage/planning.html"
    planning_name = 'bibli'
    model = ReservationBibli
    blocked_slot_model = BlockedSlotBibli

    def get_reservation_url(self, instance):
        return resolve_url("cla_reservation:manage:bibli-detail", instance.pk)

    def get_slot_url(self, instance):
        return resolve_url("cla_reservation:manage:bibli-blockedslot-update", instance.pk)

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'school_admin_planning_href': resolve_url('cla_reservation:school_admin:bibli'),
            'sync_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_reservation:manage:bibli-export')}?token={BibliIcsFileView.generate_token()}"
        })
        return context


class BibliDetailView(PlanningAdminMixin, ReservationBibliManageMixin, DetailView):
    template_name = "cla_reservation/manage/bibli/details.html"
    model = ReservationBibli
    blocked_slot_model = BlockedSlotBibli

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


class BibliUpdateView(ReservationBibliManageMixin, UpdateView):
    template_name = "cla_reservation/manage/bibli/update.html"
    model = ReservationBibli

    def get_form_class(self):
        if self.object.user:
            return ReservationBibliMemberAdminForm
        return ReservationBibliAssociationAdminForm

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:bibli-update", self.object.pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrée")
        return response


class BibliValidateView(ReservationBibliManageMixin, UpdateView):
    template_name = "cla_reservation/manage/bibli/validate.html"
    form_class = ReservationBibliValidateForm
    model = ReservationBibli

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:bibli")

    def form_valid(self, form):
        form.instance.validated_by = self.request.user
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.check_validation(self.request.user)
        messages.success(self.request, "La réservation a bien été validée")
        return response


class BibliRejectView(ReservationBibliManageMixin, UpdateView):
    template_name = "cla_reservation/manage/bibli/reject.html"
    form_class = ReservationBibliRejectForm
    model = ReservationBibli

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:bibli")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.reject("Votre réservation de la bibli a été rejetée")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response


class BibliBlockedSlotListView(ReservationBibliManageMixin, AbstractBlockedSlotListView):
    infrastructure_name = "bibli"
    infrastructure_id = "bibli"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBibli


class BibliBlockedSlotCreateView(ReservationBibliManageMixin, AbstractBlockedSlotCreateView):
    infrastructure_name = "bibli"
    infrastructure_id = "bibli"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBibli
    form_class = BlockedSlotBibliForm


class BibliBlockedSlotUpdateView(ReservationBibliManageMixin, AbstractBlockedSlotUpdateView):
    infrastructure_name = "bibli"
    infrastructure_id = "bibli"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBibli
    form_class = BlockedSlotBibliForm


class BibliBlockedSlotDeleteView(ReservationBibliManageMixin, AbstractBlockedSlotDeleteView):
    infrastructure_name = "bibli"
    infrastructure_id = "bibli"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBibli


class BibliIcsFileView(PlanningAdminMixin, JWTMixin, View):
    jwt_payload_key = "cla_reservation:manage:bibli"
    model = ReservationBibli
    blocked_slot_model = BlockedSlotBibli

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.filter(validated=True)

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        for e in self.get_planning_items(timezone.now(), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e.get('title'))
            event.add('dtstart', e.get('start'))
            event.add('dtend', e.get('end'))
            event.add('description', e.get('name'))
            event.add('location', e.get('Bibli'))
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')
