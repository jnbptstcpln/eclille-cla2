from django.shortcuts import resolve_url, render, redirect

from cla_registration.models import RegistrationSession


class CurrentRegistrationSessionMixin:
    current_registration_session: RegistrationSession = None

    def dispatch(self, request, *args, **kwargs):
        self.current_registration_session = RegistrationSession.objects.get_current_registration_session()
        if self.current_registration_session is None:
            return render(request, "cla_registration/registration/registration_closed.html")
        return super().dispatch(request, *args, **kwargs)


class InteRegistrationMixin:

    def get_success_url(self):
        return resolve_url("cla_registration:inte_paiement", self.registration.pk)

    def get_back_url(self):
        return resolve_url("cla_registration:inte")