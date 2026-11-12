from .models import Mail
from .sending import Content, content


@content(Mail.Kind.TEST)
def test(target, user):
    return Content(
        to=user.email, subject="[CLA] Mail de test",
        text="Ceci est un mail de test envoyé depuis l'admin du site. S'il est arrivé, l'envoi des mails fonctionne.",
    )
