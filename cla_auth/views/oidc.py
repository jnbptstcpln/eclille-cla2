"""
Vues OpenID Connect : celles de django-oauth-toolkit, avec les mêmes règles d'accès que l'ancien SSO
(collèges, validation du compte, consentement, connexion forcée).
"""
import time

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, resolve_url
from django.utils.http import urlencode
from oauth2_provider import views as oauth2_views
from oauth2_provider.models import get_application_model

from cla_auth.models import ServiceAuthorization
from cla_auth.views.service import render_access_error

# Date à laquelle l'utilisateur a été envoyé vers la page de connexion par ce flux
LOGIN_REQUESTED_AT = "cla_auth:oidc_login_requested_at"


class AuthorizationView(oauth2_views.AuthorizationView):
    template_name = "cla_auth/oidc/authorize.html"

    def dispatch(self, request, *args, **kwargs):
        client_id = request.POST.get("client_id", request.GET.get("client_id"))
        self.application = get_application_model().objects.filter(client_id=client_id).select_related("service").first()
        self.service = getattr(self.application, "service", None)
        if not request.user.is_authenticated:
            # La connexion qui va suivre est une connexion fraîche (cf. _login_is_fresh)
            request.session[LOGIN_REQUESTED_AT] = time.time()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.application is None:
            return super().get(request, *args, **kwargs)  # Erreur invalid_client gérée par django-oauth-toolkit
        if self.service is None:
            raise PermissionDenied("Cette application n'est liée à aucun service")

        # Ressaisie du mot de passe : demandée par le service (prompt=login) ou imposée (connexion automatique désactivée)
        login_is_fresh = self._login_is_fresh()
        if ("login" in request.GET.get("prompt", "").split() or not self.service.auto_login) and not login_is_fresh:
            request.session[LOGIN_REQUESTED_AT] = time.time()
            query = urlencode({"next": self._path_without_prompt(), "prompt": "login"})
            return redirect(f"{resolve_url(settings.LOGIN_URL)}?{query}")

        error = self.service.access_error(request.user)
        if error:
            return render_access_error(request, self.service, error, self._path_without_prompt())

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if self.service is None:
            raise PermissionDenied("Cette application n'est liée à aucun service")
        # Revérifié ici : le formulaire de consentement peut être envoyé sans passer par get()
        error = self.service.access_error(self.request.user)
        if error:
            return render_access_error(self.request, self.service, error, resolve_url("cla_public:index"))
        if form.cleaned_data.get("allow") and self.service.authorization_required:
            ServiceAuthorization.objects.get_or_create(service=self.service, user=self.request.user)
        return super().form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        # django-oauth-toolkit s'apprête à afficher l'écran de consentement : on le saute si le service
        # ne le demande pas ou si l'utilisateur l'a déjà accepté (y compris via l'ancien SSO)
        if "form" in context and not self._consent_needed():
            form = self.get_form_class()(data={**self.get_initial(), "allow": True})
            if form.is_valid():
                return self.form_valid(form)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(service=self.service, **kwargs)

    def _consent_needed(self):
        return self.service.authorization_required and not self.service.has_user_gave_authorization(self.request.user)

    def _login_is_fresh(self):
        """Vrai si l'utilisateur s'est connecté après avoir été envoyé vers la page de connexion par ce flux."""
        requested_at = self.request.session.pop(LOGIN_REQUESTED_AT, None)
        last_login = self.request.user.last_login
        return requested_at is not None and last_login is not None and last_login.timestamp() >= requested_at

    def _path_without_prompt(self):
        query = self.request.GET.copy()
        query.pop("prompt", None)
        return f"{self.request.path}?{query.urlencode()}"


class LogoutView(oauth2_views.RPInitiatedLogoutView):
    template_name = "cla_auth/oidc/logout_confirm.html"

    def do_logout(self, *args, **kwargs):
        response = super().do_logout(*args, **kwargs)
        response.delete_cookie("stay_logged_in")  # Sinon StayLoggedInMiddleware reconnecte l'utilisateur
        return response
