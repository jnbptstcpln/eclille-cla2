from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import resolve_url, redirect
from django.views import View
from django.views.generic import FormView, DeleteView

from cla_reservation.forms.barbecue import ReservationBarbecueAssociationForm
from cla_reservation.forms.bibli import ReservationBibliAssociationForm
from cla_reservation.forms.foyer import ReservationFoyerAssociationForm
from cla_reservation.forms.synthe import ReservationSyntheAssociationForm
from cla_reservation.mixins import ReservationAssociationMixin
from cla_reservation.models import BarbecueRules, ReservationBarbecue, ReservationBibli, BibliRules
from cla_reservation.models.foyer import ReservationFoyer, FoyerRules, BeerMenu
from cla_reservation.models.synthe import ReservationSynthe


class ReservationBarbecueView(LoginRequiredMixin, ReservationAssociationMixin, FormView):
    template_name = "cla_reservation/association/barbecue.html"
    model = ReservationBarbecue
    form_class = ReservationBarbecueAssociationForm
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_barbecue()

    def get_success_url(self):
        return resolve_url("cla_reservation:association:barbecue", self.association.slug, self.event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rules': BarbecueRules.objects.last()
        })
        return context


class ReservationBarbecueDeleteView(LoginRequiredMixin, ReservationAssociationMixin, View):
    model = ReservationBarbecue
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_barbecue()

    def get(self, request, *args, **kwargs):
        return redirect("cla_reservation:association:barbecue", self.association.slug, self.event.pk)

    def post(self, request, *args, **kwargs):

        if self.reservation.sent or self.reservation.validated:
            return redirect("cla_reservation:association:barbecue", self.association.slug, self.event.pk)

        self.reservation.delete()
        messages.info(self.request, "Votre réservation du barbecue a bien été supprimée")

        return redirect("cla_event:association:update", self.association.slug, self.event.pk)


class ReservationBibliView(LoginRequiredMixin, ReservationAssociationMixin, FormView):
    template_name = "cla_reservation/association/bibli.html"
    model = ReservationBibli
    form_class = ReservationBibliAssociationForm
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_bibli()

    def get_success_url(self):
        return resolve_url("cla_reservation:association:bibli", self.association.slug, self.event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rules': BibliRules.objects.last()
        })
        return context


class ReservationBibliDeleteView(LoginRequiredMixin, ReservationAssociationMixin, View):
    model = ReservationBibli
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_bibli()

    def get(self, request, *args, **kwargs):
        return redirect("cla_reservation:association:bibli", self.association.slug, self.event.pk)

    def post(self, request, *args, **kwargs):

        if self.reservation.sent or self.reservation.validated:
            return redirect("cla_reservation:association:bibli", self.association.slug, self.event.pk)

        self.reservation.delete()
        messages.info(self.request, "Votre réservation de la bibli a bien été supprimée")

        return redirect("cla_event:association:update", self.association.slug, self.event.pk)


class ReservationFoyerView(LoginRequiredMixin, ReservationAssociationMixin, FormView):
    template_name = "cla_reservation/association/foyer.html"
    model = ReservationFoyer
    form_class = ReservationFoyerAssociationForm
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_foyer()

    def get_success_url(self):
        return resolve_url("cla_reservation:association:foyer", self.association.slug, self.event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rules': FoyerRules.objects.last(),
            'beer_menu': BeerMenu.objects.last()
        })
        return context


class ReservationFoyerDeleteView(LoginRequiredMixin, ReservationAssociationMixin, View):
    model = ReservationFoyer
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_foyer()

    def get(self, request, *args, **kwargs):
        return redirect("cla_reservation:association:foyer", self.association.slug, self.event.pk)

    def post(self, request, *args, **kwargs):

        if self.reservation.sent or self.reservation.validated:
            return redirect("cla_reservation:association:foyer", self.association.slug, self.event.pk)

        self.reservation.delete()
        messages.info(self.request, "Votre réservation du foyer a bien été supprimée")

        return redirect("cla_event:association:update", self.association.slug, self.event.pk)


class ReservationSyntheView(LoginRequiredMixin, ReservationAssociationMixin, FormView):
    template_name = "cla_reservation/association/synthe.html"
    model = ReservationSynthe
    form_class = ReservationSyntheAssociationForm
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_synthe()

    def get_success_url(self):
        return resolve_url("cla_reservation:association:synthe", self.association.slug, self.event.pk)


class ReservationSyntheDeleteView(LoginRequiredMixin, ReservationAssociationMixin, View):
    model = ReservationSynthe
    creating = False
    reservation: model = None

    def get_reservation(self):
        return self.event.get_reservation_synthe()

    def get(self, request, *args, **kwargs):
        return redirect("cla_reservation:association:synthe", self.association.slug, self.event.pk)

    def post(self, request, *args, **kwargs):

        if self.reservation.sent or self.reservation.validated:
            return redirect("cla_reservation:association:synthe", self.association.slug, self.event.pk)

        self.reservation.delete()
        messages.info(self.request, "Votre réservation du synthé a bien été supprimée")

        return redirect("cla_event:association:update", self.association.slug, self.event.pk)
