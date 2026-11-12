from django.shortcuts import resolve_url

from cla_mail.models import Mail
from cla_mail.sending import absolute_url, send
from .models import UserInfos


def send_activation_email(sender, instance: UserInfos, created, **kwargs):
    """
    Envoi d'un mail de bienvenue à destination de l'utilisateur,
    automatiquement après la création de son compte sur le site.
    Ce mail contient le lien permettant l'activation du compte.
    """
    if created:
        if instance.activated_on is None:
            send(
                Mail.Kind.ACTIVATION, instance.email_school, "[CLA] Activation de votre compte",
                "Bienvenue au sein de Centrale Lille Associations",
                template="cla_auth/activation/mail.html",
                context={"activation_href": absolute_url(resolve_url("cla_auth:activate", instance.activation_jwt))},
                user=instance.user,
            )
