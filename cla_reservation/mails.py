from django.shortcuts import resolve_url

from cla_mail.models import Mail
from cla_mail.sending import Content, absolute_url, content

# Modèle de réservation -> (étiquette du sujet, complément du texte, préfixe de l'URL de gestion)
RESERVATIONS = {
    "reservationfoyer": ("FOYER", "du foyer", "foyer"),
    "reservationbarbecue": ("BARBECUE", "du barbecue", "barbecue"),
    "reservationsynthe": ("SYNTHÉ", "du synthé", "synthe"),
    "reservationdancehall": ("SALLE DE DANSE", "de la salle de danse", "dancehall"),
    "reservationbibli": ("BIBLI", "du bibli", "bibli"),
}


@content(Mail.Kind.RESERVATION_TO_VALIDATE)
def reservation_to_validate(reservation, user):
    label, name, url_prefix = RESERVATIONS[reservation._meta.model_name]
    return Content(
        to=user.email, subject=f"[CLA][{label}] Nouvelle demande de réservation",
        text=f"Une demande de réservation {name} a été reçue",
        template="cla_reservation/manage/mail.html",
        context={
            "detail_href": absolute_url(resolve_url(f"cla_reservation:manage:{url_prefix}-detail", reservation.pk)),
            "reservation": reservation,
        },
    )
