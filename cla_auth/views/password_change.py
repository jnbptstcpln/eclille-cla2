from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, resolve_url
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from cla_auth.forms.reset import ChangeRequiredPasswordForm
from cla_auth.models import must_change_password
from cla_web.middlewares import StayLoggedInMiddleware


@login_required
def password_change_required(req):
    """Page imposée par PasswordChangeRequiredMiddleware tant que le mot de passe n'a pas été changé."""
    user = req.user
    next_url = req.POST.get("next") or req.GET.get("next")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={req.get_host()}, require_https=req.is_secure()):
        next_url = resolve_url("cla_member:lobby")

    if not must_change_password(user):
        return redirect(next_url)

    if req.method == "POST":
        form = ChangeRequiredPasswordForm(req.POST, user=user)
        if form.is_valid():
            user.set_password(form.cleaned_data["password1"])
            user.save()  # enregistre aussi la date du changement (signal record_password_change)
            update_session_auth_hash(req, user)  # reste connecté malgré le nouveau mot de passe

            response = redirect(next_url)
            if "stay_logged_in" in req.COOKIES:
                # L'ancien cookie « rester connecté » dépend de l'ancien mot de passe : on le renouvelle
                response.set_cookie(
                    "stay_logged_in", StayLoggedInMiddleware.get_jwt(user),
                    expires=timezone.datetime.utcnow() + timezone.timedelta(days=30),
                )
            return response
    else:
        form = ChangeRequiredPasswordForm(user=user)

    return render(req, "cla_auth/session/password_change_required.html", {"form": form, "next": next_url})
