from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import resolve_url
from django.template.loader import render_to_string


def send_activation_email(sender, instance: User, created, **kwargs):
    """
    Envoi d'un mail de bienvenue à destination de l'utilisateur,
    automatiquement après la création de son compte sur le site.
    Ce mail contient le lien permettant l'activation du compte.
    """
    if created:
        if hasattr(instance, 'infos'):
            if instance.infos.activated_on is None:
                send_mail(
                    subject='Activation de votre compte CLA',
                    from_email=settings.EMAIL_HOST_FROM,
                    recipient_list=[instance.infos.email_school],
                    message="Bienvenue au sein de Centrale Lille Association",
                    html_message=render_to_string(
                        'cla_auth/activation/mail.html',
                        {
                            'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                            'activation_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_auth:activate', instance.infos.activation_jwt)}",
                        }
                    ),
                )