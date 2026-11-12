from cla_mail.models import Mail
from cla_mail.sending import send
from .models import UserInfos


def send_activation_email(sender, instance: UserInfos, created, **kwargs):
    """
    Envoi d'un mail de bienvenue à destination de l'utilisateur,
    automatiquement après la création de son compte sur le site.
    Ce mail contient le lien permettant l'activation du compte.
    """
    if created:
        if instance.activated_on is None:
            send(Mail.Kind.ACTIVATION, target=instance, user=instance.user)
