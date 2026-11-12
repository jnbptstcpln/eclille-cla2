import logging

import jwt

from django.contrib import auth, messages
from django.shortcuts import render, redirect, reverse, resolve_url
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from cla_web.middlewares import StayLoggedInMiddleware
from cla_auth.models import PasswordResetRequest
from cla_auth.forms.session import LoginForm, ForgotForm
from cla_mail.models import Mail
from cla_mail.sending import send

logger = logging.getLogger(__name__)


@csrf_protect
def login(req):
    if req.user.is_authenticated:
        return redirect(req.GET.get("next", "cla_member:lobby"))

    if req.method == "POST":
        form = LoginForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            req.session["next"] = form.cleaned_data["redirect"]
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)

                response = redirect(req.session.get("next", None) or "cla_member:lobby")

                if hasattr(user, "infos"):
                    # Check if the account lost its validation since last login
                    if user.infos.valid_until is not None:
                        if (
                            user.last_login <= user.infos.valid_until <= timezone.now()
                            and req.session.get("validation_alert", True)
                        ):
                            response = render(
                                req,
                                "cla_auth/validation/validate_alert_standalone.html",
                                {
                                    "redirect": resolve_url(
                                        req.session.get("next", "cla_member:lobby")
                                    )
                                },
                            )

                # Handle stay_logged_in
                if form.cleaned_data["stay_logged_in"]:
                    response.set_cookie(
                        "stay_logged_in",
                        StayLoggedInMiddleware.get_jwt(user),
                        expires=timezone.datetime.utcnow()
                        + timezone.timedelta(days=30),
                    )

                return response

            else:
                form.add_error(None, "Combinaison identifiant/mot de passe incorrecte")
    else:
        req.session["next"] = req.GET.get("next", "cla_member:lobby")
        req.session["validation_alert"] = req.GET.get("validation_alert", "1") == "1"
        form = LoginForm(initial={"redirect": req.session["next"]})

    return render(req, "cla_auth/session/login.html", {"form": form})


def forgot(req):
    if req.user.is_authenticated:
        return redirect("cla_member:lobby")

    return render(req, "cla_auth/session/forgot.html")


def forgot_username(req):
    if req.user.is_authenticated:
        return redirect("cla_member:lobby")

    username = None
    server_error = False
    if req.method == "POST":
        form = ForgotForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            if users.count() == 1:
                user = users.first()
                username = user.username
            elif users.count() > 1:
                server_error = True
                logger.error("« J'ai oublié mon identifiant » : plusieurs comptes utilisateur ont l'adresse %s", email)
    else:
        form = ForgotForm()

    return render(
        req,
        "cla_auth/session/forgot_username.html",
        {"username": username, "form": form, "server_error": server_error},
    )


def forgot_password(req):
    if req.user.is_authenticated:
        return redirect("cla_member:lobby")

    error = None
    warning = None
    success = None
    server_error = False

    if req.method == "POST":
        form = ForgotForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            users = User.objects.filter(email=email)
            if users.count() == 1:
                user = users.first()
                reset_req: PasswordResetRequest = (
                    PasswordResetRequest.objects.get_or_create_reset_request(user=user)
                )
                if (
                    reset_req.attempt < 3
                ):  # Send reset email if less than 3 attempts were made
                    send(Mail.Kind.PASSWORD_RESET, target=reset_req, user=user)
                    success = True
                else:
                    warning = True
            elif users.count() > 1:
                server_error = True
                logger.error("« J'ai oublié mon mot de passe » : plusieurs comptes utilisateur ont l'adresse %s", email)

    else:
        form = ForgotForm()

    return render(
        req,
        "cla_auth/session/forgot_password.html",
        {
            "form": form,
            "error": error,
            "warning": warning,
            "success": success,
            "server_error": server_error,
        },
    )


def logout(req):
    auth.logout(req)
    response = redirect("cla_public:index")
    response.delete_cookie("stay_logged_in")
    return response
