from django.shortcuts import resolve_url

from cla_mail.models import Mail
from cla_mail.sending import Content, absolute_url, content


@content(Mail.Kind.ACTIVATION)
def activation(infos, user):
    return Content(
        to=infos.email_school, subject="[CLA] Activation de votre compte",
        text="Bienvenue au sein de Centrale Lille Associations",
        template="cla_auth/activation/mail.html",
        context={"activation_href": absolute_url(resolve_url("cla_auth:activate", infos.activation_jwt))},
    )


@content(Mail.Kind.PASSWORD_RESET)
def password_reset(reset_request, user):
    return Content(
        to=user.email, subject="[CLA] Réinitialiser votre mot de passe",
        text="Réinitialiser le mot de passe de votre compte CLA",
        template="cla_auth/reset/mail.html",
        context={"reset_href": absolute_url(resolve_url("cla_auth:reset", reset_request.get_reset_jwt()))},
    )


@content(Mail.Kind.ACCOUNT_VALIDATION)
def account_validation(validation_request, user):
    return Content(
        to=user.infos.email_school, subject="[CLA] Validation de votre compte",
        text=f"Voici le code à indiquer pour valider votre compte : {validation_request.code}",
        template="cla_auth/validation/mail.html",
        context={
            "validation_href": absolute_url(resolve_url("cla_auth:validate")),
            "validation_request": validation_request,
        },
    )
