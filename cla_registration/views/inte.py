from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, TemplateView

from cla_registration.mixins import CurrentRegistrationSessionMixin, InteRegistrationMixin
from cla_registration.models import RegistrationSession, Registration
from cla_registration.views.user import CentralePackRegistrationView, CentralePackDDRegistrationView, CentraleCLARegistrationView, CentraleCLADDRegistrationView


class IndexView(CurrentRegistrationSessionMixin, TemplateView):
    current_registration_session: RegistrationSession = None
    template_name = "cla_registration/inte/index.html"


class PackRegistrationView(InteRegistrationMixin, CentralePackRegistrationView):
    pass


class PackDDRegistrationView(InteRegistrationMixin, CentralePackDDRegistrationView):
    pass


class CLARegistrationView(InteRegistrationMixin, CentraleCLARegistrationView):
    pass


class CLADDRegistrationView(InteRegistrationMixin, CentraleCLADDRegistrationView):
    pass


class RegistrationPaiementView(DetailView):
    model = Registration
    template_name = "cla_registration/inte/paiement.html"
