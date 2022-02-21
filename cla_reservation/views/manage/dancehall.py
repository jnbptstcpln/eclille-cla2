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
from cla_reservation.forms.dancehall import ReservationDanceHallRejectForm, ReservationDanceHallValidateForm, ReservationDanceHallAssociationAdminForm, ReservationDanceHallMemberAdminForm, BlockedSlotDanceHallForm
from cla_reservation.mixins import ReservationDanceHallManageMixin, PlanningAdminMixin
from cla_reservation.models import ReservationDanceHall
from cla_reservation.models.dancehall import BlockedSlotDanceHall
from cla_reservation.views._blockedslot import AbstractBlockedSlotListView, AbstractBlockedSlotCreateView, AbstractBlockedSlotUpdateView, AbstractBlockedSlotDeleteView


class DanceHallListView(ReservationDanceHallManageMixin, ListView):
    template_name = "cla_reservation/manage/dancehall/list.html"
    model = ReservationDanceHall
    queryset = ReservationDanceHall.objects.filter(validated=True, sent=True)
    paginate_by = 20


class DanceHallPlanningView(PlanningAdminMixin, ReservationDanceHallManageMixin, TemplateView):
    cla_reservation_active_section = "planning"
    template_name = "cla_reservation/manage/planning.html"
    planning_name = 'synthé'
    model = ReservationDanceHall
    blocked_slot_model = BlockedSlotDanceHall

    def get_reservation_url(self, instance):
        return resolve_url("cla_reservation:manage:dancehall-detail", instance.pk)

    def get_slot_url(self, instance):
        return resolve_url("cla_reservation:manage:dancehall-blockedslot-update", instance.pk)

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'school_admin_planning_href': resolve_url('cla_reservation:school_admin:dancehall'),
            'sync_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_reservation:manage:dancehall-export')}?token={DanceHallIcsFileView.generate_token()}"
        })
        return context


class DanceHallDetailView(PlanningAdminMixin, ReservationDanceHallManageMixin, DetailView):
    template_name = "cla_reservation/manage/dancehall/details.html"
    model = ReservationDanceHall
    blocked_slot_model = BlockedSlotDanceHall

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


class DanceHallUpdateView(ReservationDanceHallManageMixin, UpdateView):
    template_name = "cla_reservation/manage/dancehall/update.html"
    model = ReservationDanceHall

    def get_form_class(self):
        if self.object.user:
            return ReservationDanceHallMemberAdminForm
        return ReservationDanceHallAssociationAdminForm

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:dancehall-update", self.object.pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrée")
        return response


class DanceHallValidateView(ReservationDanceHallManageMixin, UpdateView):
    template_name = "cla_reservation/manage/dancehall/validate.html"
    form_class = ReservationDanceHallValidateForm
    model = ReservationDanceHall

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:dancehall")

    def form_valid(self, form):
        form.instance.validated_by = self.request.user
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.check_validation(self.request.user)
        messages.success(self.request, "La réservation a bien été validée")
        return response


class DanceHallRejectView(ReservationDanceHallManageMixin, UpdateView):
    template_name = "cla_reservation/manage/dancehall/reject.html"
    form_class = ReservationDanceHallRejectForm
    model = ReservationDanceHall

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:dancehall")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.reject("Votre réservation du synthé a été rejetée")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response



class BlockSlotBarbecueListView(ReservationDanceHallManageMixin, UpdateView):
    template_name = "cla_reservation/manage/dancehall/reject.html"
    form_class = ReservationDanceHallRejectForm
    model = ReservationDanceHall

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:dancehall")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.reject("Votre réservation du synthé a été rejetée")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response



class DanceHallBlockedSlotListView(ReservationDanceHallManageMixin, AbstractBlockedSlotListView):
    infrastructure_name = "dancehall"
    infrastructure_id = "dancehall"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotDanceHall


class DanceHallBlockedSlotCreateView(ReservationDanceHallManageMixin, AbstractBlockedSlotCreateView):
    infrastructure_name = "dancehall"
    infrastructure_id = "dancehall"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotDanceHall
    form_class = BlockedSlotDanceHallForm


class DanceHallBlockedSlotUpdateView(ReservationDanceHallManageMixin, AbstractBlockedSlotUpdateView):
    infrastructure_name = "dancehall"
    infrastructure_id = "dancehall"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotDanceHall
    form_class = BlockedSlotDanceHallForm


class DanceHallBlockedSlotDeleteView(ReservationDanceHallManageMixin, AbstractBlockedSlotDeleteView):
    infrastructure_name = "dancehall"
    infrastructure_id = "dancehall"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotDanceHall


class DanceHallIcsFileView(PlanningAdminMixin, JWTMixin, View):
    jwt_payload_key = "cla_reservation:manage:dancehall"
    model = ReservationDanceHall
    blocked_slot_model = BlockedSlotDanceHall

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
            event.add('location', e.get('Barbecue'))
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')
