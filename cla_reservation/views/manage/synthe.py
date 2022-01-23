from django.contrib import messages
from django.shortcuts import resolve_url
from django.views.generic import ListView, DetailView, UpdateView, TemplateView

from cla_reservation.forms.synthe import ReservationSyntheRejectForm, ReservationSyntheValidateForm, ReservationSyntheAssociationAdminForm, ReservationSyntheMemberAdminForm, BlockedSlotSyntheForm
from cla_reservation.mixins import ReservationSyntheManageMixin, PlanningAdminMixin
from cla_reservation.models import ReservationSynthe
from cla_reservation.models.synthe import BlockedSlotSynthe
from cla_reservation.views._blockedslot import AbstractBlockedSlotListView, AbstractBlockedSlotCreateView, AbstractBlockedSlotUpdateView, AbstractBlockedSlotDeleteView


class SyntheListView(ReservationSyntheManageMixin, ListView):
    template_name = "cla_reservation/manage/synthe/list.html"
    model = ReservationSynthe
    queryset = ReservationSynthe.objects.filter(validated=True, sent=True)
    paginate_by = 20


class SynthePlanningView(PlanningAdminMixin, ReservationSyntheManageMixin, TemplateView):
    cla_reservation_active_section = "planning"
    template_name = "cla_reservation/manage/planning.html"
    planning_name = 'synthé'
    model = ReservationSynthe
    blocked_slot_model = BlockedSlotSynthe

    def get_reservation_url(self, instance):
        return resolve_url("cla_reservation:manage:synthe-detail", instance.pk)

    def get_slot_url(self, instance):
        return resolve_url("cla_reservation:manage:synthe-blockedslot-update", instance.pk)

    def get_blocked_slot_base_queryset(self):
        return self.blocked_slot_model.objects.all()

    def get_reservation_base_queryset(self):
        return self.model.objects.all()


class SyntheDetailView(PlanningAdminMixin, ReservationSyntheManageMixin, DetailView):
    template_name = "cla_reservation/manage/synthe/details.html"
    model = ReservationSynthe
    blocked_slot_model = BlockedSlotSynthe

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


class SyntheUpdateView(ReservationSyntheManageMixin, UpdateView):
    template_name = "cla_reservation/manage/synthe/update.html"
    model = ReservationSynthe

    def get_form_class(self):
        if self.object.user:
            return ReservationSyntheMemberAdminForm
        return ReservationSyntheAssociationAdminForm

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:synthe-update", self.object.pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrée")
        return response


class SyntheValidateView(ReservationSyntheManageMixin, UpdateView):
    template_name = "cla_reservation/manage/synthe/validate.html"
    form_class = ReservationSyntheValidateForm
    model = ReservationSynthe

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:synthe")

    def form_valid(self, form):
        form.instance.validated_by = self.request.user
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.check_validation(self.request.user)
        messages.success(self.request, "La réservation a bien été validée")
        return response


class SyntheRejectView(ReservationSyntheManageMixin, UpdateView):
    template_name = "cla_reservation/manage/synthe/reject.html"
    form_class = ReservationSyntheRejectForm
    model = ReservationSynthe

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:synthe")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.reject("Votre réservation du synthé a été rejeté")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response



class BlockSlotBarbecueListView(ReservationSyntheManageMixin, UpdateView):
    template_name = "cla_reservation/manage/synthe/reject.html"
    form_class = ReservationSyntheRejectForm
    model = ReservationSynthe

    def get_success_url(self):
        return resolve_url("cla_reservation:manage:synthe")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.event:
            form.instance.event.reject("Votre réservation du synthé a été rejeté")
        messages.success(self.request, "La réservation a bien été rejetée")
        return response



class SyntheBlockedSlotListView(ReservationSyntheManageMixin, AbstractBlockedSlotListView):
    infrastructure_name = "synthe"
    infrastructure_id = "synthe"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotSynthe


class SyntheBlockedSlotCreateView(ReservationSyntheManageMixin, AbstractBlockedSlotCreateView):
    infrastructure_name = "synthe"
    infrastructure_id = "synthe"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotSynthe
    form_class = BlockedSlotSyntheForm


class SyntheBlockedSlotUpdateView(ReservationSyntheManageMixin, AbstractBlockedSlotUpdateView):
    infrastructure_name = "synthe"
    infrastructure_id = "synthe"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotSynthe
    form_class = BlockedSlotSyntheForm


class SyntheBlockedSlotDeleteView(ReservationSyntheManageMixin, AbstractBlockedSlotDeleteView):
    infrastructure_name = "synthe"
    infrastructure_id = "synthe"

    cla_reservation_active_section = "blockedslot"
    model = BlockedSlotSynthe