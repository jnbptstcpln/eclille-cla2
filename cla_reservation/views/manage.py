from django.contrib import messages
from django.shortcuts import resolve_url
from django.views.generic import TemplateView, ListView, DetailView, UpdateView

from cla_reservation.forms.barbecue import ReservationBarbecueAssociationAdminForm, ReservationBarbecueValidateForm, ReservationBarbecueRejectForm, ReservationBarbecueMemberAdminForm
from cla_reservation.forms.foyer import ReservationFoyerAdminForm, ReservationFoyerValidateForm, ReservationFoyerRejectForm
from cla_reservation.forms.synthe import ReservationSyntheRejectForm, ReservationSyntheValidateForm, ReservationSyntheAssociationAdminForm, ReservationSyntheMemberAdminForm
from cla_reservation.mixins import ReservationManageMixin, ReservationFoyerManageMixin, ReservationBarbecueManageMixin, ReservationSyntheManageMixin
from cla_reservation.models import ReservationBarbecue, ReservationFoyer, ReservationSynthe


class IndexView(ReservationManageMixin, TemplateView):
    association_manage_active_section = "index"
    template_name = "cla_reservation/manage/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'to_review_barbecue': ReservationBarbecue.objects.to_validate(),
            'to_review_foyer': ReservationFoyer.objects.to_validate(),
            'to_review_synthe': ReservationSynthe.objects.to_validate()
        })
        return context


class FoyerListView(ReservationFoyerManageMixin, ListView):
    template_name = "cla_reservation/manage/foyer/list.html"
    model = ReservationFoyer
    queryset = ReservationFoyer.objects.filter(validated=True, sent=True)
    paginate_by = 20


class FoyerDetailView(ReservationFoyerManageMixin, DetailView):
    template_name = "cla_reservation/manage/foyer/details.html"
    model = ReservationFoyer


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


class BarbecueListView(ReservationBarbecueManageMixin, ListView):
    template_name = "cla_reservation/manage/barbecue/list.html"
    model = ReservationBarbecue
    queryset = ReservationBarbecue.objects.filter(validated=True, sent=True)
    paginate_by = 20


class BarbecueDetailView(ReservationBarbecueManageMixin, DetailView):
    template_name = "cla_reservation/manage/barbecue/details.html"
    model = ReservationBarbecue


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


class SyntheListView(ReservationSyntheManageMixin, ListView):
    template_name = "cla_reservation/manage/synthe/list.html"
    model = ReservationSynthe
    queryset = ReservationSynthe.objects.filter(validated=True, sent=True)
    paginate_by = 20


class SyntheDetailView(ReservationSyntheManageMixin, DetailView):
    template_name = "cla_reservation/manage/synthe/details.html"
    model = ReservationSynthe


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
