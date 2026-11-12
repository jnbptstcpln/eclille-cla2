from django.contrib.auth.models import User
from django.utils import timezone

from cla_mail.models import Mail
from cla_mail.sending import send
from .models import PasswordChange, UserInfos


def send_activation_email(sender, instance: UserInfos, created, **kwargs):
    """
    Envoi d'un mail de bienvenue à destination de l'utilisateur,
    automatiquement après la création de son compte sur le site.
    Ce mail contient le lien permettant l'activation du compte.
    """
    if created:
        if instance.activated_on is None:
            send(Mail.Kind.ACTIVATION, target=instance, user=instance.user)


def record_password_change(sender, instance: User, created, **kwargs):
    """
    Note la date de chaque changement de mot de passe :
    - `_password` n'est renseigné par Django que lorsque `set_password` vient d'être appelé
      (activation, mot de passe oublié, admin…) ;
    - un compte créé directement avec un mot de passe (create_user, createsuperuser) a lui aussi
      un mot de passe neuf.
    """
    password_set = getattr(instance, "_password", None) is not None
    created_with_password = created and instance.password and instance.has_usable_password()
    if password_set or created_with_password:
        PasswordChange.objects.update_or_create(user=instance, defaults={"changed_on": timezone.now()})
