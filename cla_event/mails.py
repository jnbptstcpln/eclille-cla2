from django.shortcuts import resolve_url

from cla_mail.models import Mail
from cla_mail.sending import Content, absolute_url, content


@content(Mail.Kind.EVENT_TO_VALIDATE)
def event_to_validate(event, user):
    return Content(
        to=user.email, subject="[CLA] Nouvel événement à valider",
        text="Une demande de validation d'événement a été reçue",
        template="cla_event/manage/mail.html",
        context={"detail_href": absolute_url(resolve_url("cla_event:manage:event-detail", event.pk)), "event": event},
    )
