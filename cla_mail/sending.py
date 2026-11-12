"""
Point d'entrée unique pour envoyer un mail depuis le site.

Chaque envoi est inscrit dans le journal des mails (admin > Mails > Journal des mails),
qu'il ait réussi ou non. Les fonctions ne lèvent jamais d'exception : l'appelant regarde
`mail.status` pour savoir s'il doit prévenir l'utilisateur.

Exemple :
    mail = send(
        Mail.Kind.PASSWORD_RESET, user.email, "[CLA] Réinitialiser votre mot de passe",
        text="Réinitialiser le mot de passe de votre compte CLA",
        template="cla_auth/reset/mail.html", context={"reset_href": ...}, user=user,
    )
    if mail.status == Mail.Status.FAILED:
        ...
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Mail

logger = logging.getLogger(__name__)


def absolute_url(path=""):
    """Lien absolu vers le site, pour les liens placés dans les mails."""
    return f"https://{settings.ALLOWED_HOSTS[0]}{path}"


def send(kind, to, subject, text, template=None, context=None, user=None) -> Mail:
    """
    Envoie un mail à un seul destinataire et l'inscrit dans le journal.

    - `text` : version texte brut du mail (affichée par les clients qui n'affichent pas le HTML).
    - `template` : template HTML optionnel, qui reçoit `context` et `site_href`.
    - Les réponses éventuelles vont à l'adresse de contact (CONTACT_EMAIL), pas au noreply.
    """
    mail = Mail(kind=kind, recipient=to, user=user, subject=subject)
    try:
        message = EmailMultiAlternatives(
            subject=subject, body=text, from_email=settings.EMAIL_HOST_FROM,
            to=[to], reply_to=[settings.CONTACT_EMAIL],
        )
        if template:
            html = render_to_string(template, {"site_href": absolute_url(), **(context or {})})
            message.attach_alternative(html, "text/html")
        message.send()
    except Exception as e:
        mail.status = Mail.Status.FAILED
        mail.error = f"{type(e).__name__} : {e}"
        logger.exception("Mail « %s » non envoyé à %s", kind, to)
    else:
        mail.status = Mail.Status.SENT
        mail.sent_on = timezone.now()
    mail.save()
    return mail


def send_to_users(kind, users, subject, text, template=None, context=None) -> list[Mail]:
    """
    Envoie le même mail à plusieurs utilisateurs, un mail par personne :
    chacun ne voit que sa propre adresse. Les utilisateurs sans adresse sont ignorés.
    """
    return [
        send(kind, user.email, subject, text, template=template, context=context, user=user)
        for user in users if user.email
    ]


def users_with_permission(app_label, codename):
    """Utilisateurs actifs qui ont la permission `app_label.codename` par l'un de leurs groupes."""
    return get_user_model().objects.filter(
        is_active=True,
        groups__permissions__content_type__app_label=app_label,
        groups__permissions__codename=codename,
    ).distinct()
