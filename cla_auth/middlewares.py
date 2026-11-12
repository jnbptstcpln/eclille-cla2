from django.conf import settings
from django.shortcuts import redirect
from django.urls import Resolver404, resolve, reverse
from django.utils.http import urlencode

from cla_auth.models import must_change_password

# Pages accessibles avant d'avoir changé son mot de passe
ALLOWED_URL_NAMES = {"cla_auth:password_change_required", "cla_auth:logout"}


class PasswordChangeRequiredMiddleware:
    """
    Tant qu'un utilisateur connecté n'a pas choisi de nouveau mot de passe (voir PasswordChange),
    toutes les pages le renvoient vers la page de changement de mot de passe, y compris l'admin
    et les connexions aux services. Il revient ensuite sur la page qu'il voulait ouvrir.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_allowed(request) and must_change_password(request.user):
            url = reverse("cla_auth:password_change_required")
            if request.method == "GET":
                url += "?" + urlencode({"next": request.get_full_path()})
            return redirect(url)
        return self.get_response(request)

    @staticmethod
    def _is_allowed(request):
        if request.path.startswith((settings.STATIC_URL, settings.MEDIA_URL)):
            return True
        try:
            return resolve(request.path_info).view_name in ALLOWED_URL_NAMES
        except Resolver404:
            return False
