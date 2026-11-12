"""
Point d'entrée unique pour envoyer un mail depuis le site.

Chaque type de mail (Mail.Kind) a sa fonction de contenu, déclarée avec @content(kind) dans le
fichier `mails.py` de son app. Elle reçoit l'objet concerné (`target`) et l'utilisateur, et renvoie
un Content : destinataire, sujet, texte brut et template HTML.

Le contenu n'est jamais enregistré en base, car il contient des liens et des codes secrets. Un mail
mis en attente ne garde qu'une référence vers l'objet concerné : son contenu est reconstruit au
moment de l'envoi.

Quota (offre gratuite Brevo : 300 mails par jour) :
- les mails urgents (mot de passe oublié, code de validation, test) partent toujours tout de suite ;
- les mails qui peuvent attendre (activation, alertes aux responsables) partent tout de suite tant
  que le nombre de mails envoyés aujourd'hui reste sous MAIL_DAILY_LIMIT - MAIL_URGENT_RESERVE.
  Au-delà, ils sont mis en attente et envoyés par la commande `python manage.py send_pending_mails`
  (tâche planifiée Coolify) dès que le quota le permet.

Les fonctions ne lèvent jamais d'exception : l'appelant regarde `mail.status`.

Exemple :
    mail = send(Mail.Kind.PASSWORD_RESET, target=reset_request, user=user)
    if mail.status == Mail.Status.FAILED:
        ...
"""
import logging
from dataclasses import dataclass, field

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Mail

logger = logging.getLogger(__name__)

DEFERRABLE_KINDS = {Mail.Kind.ACTIVATION, Mail.Kind.EVENT_TO_VALIDATE, Mail.Kind.RESERVATION_TO_VALIDATE}


@dataclass
class Content:
    to: str
    subject: str
    text: str
    template: str = None
    context: dict = field(default_factory=dict)


_content_builders = {}


def content(kind):
    """Déclare la fonction `(target, user) -> Content` qui construit les mails de type `kind`."""
    def register(builder):
        _content_builders[kind] = builder
        return builder
    return register


def absolute_url(path=""):
    """Lien absolu vers le site, pour les liens placés dans les mails."""
    return f"https://{settings.ALLOWED_HOSTS[0]}{path}"


def sent_today():
    """Nombre de mails réellement envoyés depuis minuit."""
    midnight = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    return Mail.objects.filter(status=Mail.Status.SENT, sent_on__gte=midnight).count()


def deferrable_budget():
    """Nombre de mails « qui peuvent attendre » encore envoyables aujourd'hui."""
    return max(0, settings.MAIL_DAILY_LIMIT - settings.MAIL_URGENT_RESERVE - sent_today())


def send(kind, target=None, user=None) -> Mail:
    """Envoie un mail (ou le met en attente) et l'inscrit dans le journal."""
    mail = Mail(kind=kind, user=user, target=target)
    try:
        built = _content_builders[kind](target, user)
    except Exception as e:
        _record_failure(mail, e)
        return mail
    mail.recipient, mail.subject = built.to, built.subject

    if kind in DEFERRABLE_KINDS and deferrable_budget() <= 0:
        mail.status = Mail.Status.PENDING
        mail.save()
        return mail

    deliver(mail, built)
    return mail


def send_to_users(kind, users, target=None) -> list[Mail]:
    """
    Envoie le même type de mail à plusieurs utilisateurs, un mail par personne :
    chacun ne voit que sa propre adresse. Les utilisateurs sans adresse sont ignorés.
    """
    return [send(kind, target=target, user=user) for user in users if user.email]


def deliver(mail, built=None) -> bool:
    """
    Envoie un mail du journal (nouveau, en attente ou à renvoyer) et enregistre le résultat.
    Sans `built`, le contenu est reconstruit à partir de l'objet concerné.
    """
    mail.attempts += 1
    try:
        if built is None:
            built = _build(mail)
            mail.recipient, mail.subject = built.to, built.subject
        message = EmailMultiAlternatives(
            subject=built.subject, body=built.text, from_email=settings.EMAIL_HOST_FROM,
            to=[built.to], reply_to=[settings.CONTACT_EMAIL],
        )
        if built.template:
            html = render_to_string(built.template, {"site_href": absolute_url(), **built.context})
            message.attach_alternative(html, "text/html")
        message.send()
    except Exception as e:
        _record_failure(mail, e)
        return False
    mail.status = Mail.Status.SENT
    mail.sent_on = timezone.now()
    mail.error = ""
    mail.save()
    return True


def users_with_permission(app_label, codename):
    """Utilisateurs actifs qui ont la permission `app_label.codename` par l'un de leurs groupes."""
    return get_user_model().objects.filter(
        is_active=True,
        groups__permissions__content_type__app_label=app_label,
        groups__permissions__codename=codename,
    ).distinct()


def _build(mail):
    target = None
    if mail.content_type_id:
        target = mail.target
        if target is None:
            raise LookupError("l'objet concerné par ce mail a été supprimé")
    return _content_builders[mail.kind](target, mail.user)


def _record_failure(mail, error):
    mail.status = Mail.Status.FAILED
    mail.error = f"{type(error).__name__} : {error}"
    # warning et non error : l'échec est déjà visible dans le journal des mails, pas dans celui des erreurs
    logger.warning("Mail « %s » non envoyé à %s", mail.kind, mail.recipient or mail.user, exc_info=True)
    mail.save()
