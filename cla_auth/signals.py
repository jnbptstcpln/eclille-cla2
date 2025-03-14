from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import resolve_url
from django.template.loader import render_to_string

from .models import UserInfos


def send_activation_email(sender, instance: UserInfos, created, **kwargs):
    """
    Envoi d'un mail de bienvenue à destination de l'utilisateur,
    automatiquement après la création de son compte sur le site.
    Ce mail contient le lien permettant l'activation du compte.
    """
    if created:
        if instance.activated_on is None:
            try:
                send_mail(
                    subject='[CLA] Activation de votre compte',
                    from_email=settings.EMAIL_HOST_FROM,
                    recipient_list=[instance.email_school],
                    message="Bienvenue au sein de Centrale Lille Associations",
                    html_message=render_to_string(
                        'cla_auth/activation/mail.html',
                        {
                            'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                            'activation_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_auth:activate', instance.activation_jwt)}",
                        }
                    ),
                )
            except Exception as e:
                send_mail(
                    subject=f'[ACTIVATION] Erreur lors de l\'envoie à {instance.email_school}',
                    from_email=settings.EMAIL_HOST_FROM,
                    recipient_list=[settings.EMAIL_HOST_FROM],
                    message=f"Une erreur s'est produite lors de l'envoi du mail d'activation à {instance.email_school} : {e}"
                )
