from django.contrib import messages
from django.shortcuts import resolve_url
from django.views.generic import ListView, DetailView, UpdateView, TemplateView

from cla_reservation.forms.barbecue import ReservationBarbecueAssociationAdminForm, ReservationBarbecueValidateForm, ReservationBarbecueRejectForm, ReservationBarbecueMemberAdminForm, BlockedSlotBarbecueForm
from cla_reservation.mixins import ReservationBarbecueManageMixin, PlanningAdminMixin
from cla_reservation.models import ReservationBarbecue
from cla_reservation.models.barbecue import BlockedSlotBarbecue
from cla_reservation.views._blockedslot import AbstractBlockedSlotListView, AbstractBlockedSlotCreateView, AbstractBlockedSlotUpdateView, AbstractBlockedSlotDeleteView


class BarbecueListView(ReservationBarbecueManageMixin, ListView):
    template_name = "cla_reservation/manage/barbecue/list.html"
    model = ReservationBarbecue
    queryset = ReservationBarbecue.objects.filter(validated=True, sent=True)
    paginate_by = 20


class BarbecuePlanningView(PlanningAdminMixin, ReservationBarbecueManageMixin, TemplateView):
    cla_reservation_active_section = "planning"
    template_name = "cla_reservation/manage/planning.html"
    planning_name = 'barbecue'
    model = ReservationBarbecue
    blocked_slot_model = BlockedSlotBarbecue

    def get_reservation_url(self, instance):
        return resolve_url("cla_reservation:manage:barbecue-detail", instance.pk)

    def get_slot_url(self, instance):
        return resolve_url("cla_reservation:manage:barbecue-blockedslot-update", instance.pk)

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.all()


class BarbecueDetailView(PlanningAdminMixin, ReservationBarbecueManageMixin, DetailView):
    template_name = "cla_reservation/manage/barbecue/details.html"
    model = ReservationBarbecue
    blocked_slot_model = BlockedSlotBarbecue

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


class BarbecueUpdateView(ReservationBarbecueManageMixin, UpdateView):
    template_name = "cla_reservation/manage/barbecue/update.html"
    model = ReservationBarbecue

    def get_form_class(self):
        if self.object.user:
            return ReservationBarbecueMemberAdminForm
        return ReservationBarbecueAssociationAdminForm

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:barbecue-update", self.object.pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrée")
        return response


class BarbecueValidateView(ReservationBarbecueManageMixin, UpdateView):
    template_name = "cla_reservation/manage/barbecue/validate.html"
    form_class = ReservationBarbecueValidateForm
    model = ReservationBarbecue

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:barbecue")

    def form_valid(self, form):
        form.instance.validated_by = self.request.user
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.check_validation(self.request.user)
        messages.success(self.request, "La réservation a bien été validée")
        return response


class BarbecueRejectView(ReservationBarbecueManageMixin, UpdateView):
    template_name = "cla_reservation/manage/barbecue/reject.html"
    form_class = ReservationBarbecueRejectForm
    model = ReservationBarbecue

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:barbecue")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.reject("Votre réservation du barbecue a été rejeté")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response


class BarbecueBlockedSlotListView(ReservationBarbecueManageMixin, AbstractBlockedSlotListView):
    infrastructure_name = "barbecue"
    infrastructure_id = "barbecue"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBarbecue


class BarbecueBlockedSlotCreateView(ReservationBarbecueManageMixin, AbstractBlockedSlotCreateView):
    infrastructure_name = "barbecue"
    infrastructure_id = "barbecue"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBarbecue
    form_class = BlockedSlotBarbecueForm


class BarbecueBlockedSlotUpdateView(ReservationBarbecueManageMixin, AbstractBlockedSlotUpdateView):
    infrastructure_name = "barbecue"
    infrastructure_id = "barbecue"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBarbecue
    form_class = BlockedSlotBarbecueForm


class BarbecueBlockedSlotDeleteView(ReservationBarbecueManageMixin, AbstractBlockedSlotDeleteView):
    infrastructure_name = "barbecue"
    infrastructure_id = "barbecue"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotBarbecue
