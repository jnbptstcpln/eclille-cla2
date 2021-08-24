import csv
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from cla_registration.models import RegistrationSession, DataSharingLogs
from cla_registration.strings import RGPD_AGREEMENT_ALUMNI


class RegistrationsAlumniView(TemplateView):
    session: RegistrationSession = None
    template_name = "cla_registration/sharing/alumni.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.session = get_object_or_404(RegistrationSession, pk=kwargs.pop("session_pk", None), sharing_uuid_alumni=kwargs.pop("sharing_uuid", None))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        DataSharingLogs.objects.create(
            session=self.session,
            download_by=DataSharingLogs.Organism.ALUMNI
        )

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Campagne d\'adhésion '+str(self.session.school_year)+'.csv"'},
        )

        fields = {
            "Nom": lambda x: x.last_name,
            "Prénom": lambda x: x.first_name,
            "Adresse mail": lambda x: x.email,
            "Adresse mail école": lambda x: x.email_school,
            "Numéro de téléphone": lambda x: x.phone,
            "Date de naissance": lambda x: x.birthdate,
            "Ecole": lambda x: x.school,
            "Double diplôme entrant": lambda x: f"Oui ({x.original_school})" if x.original_school is not None else "Non",
            "Montant de la cotisation": lambda x: f"{x.contribution}€",
            "A choisi le pack (a cotisé pour adhérer à Centrale Lille Alumni)": lambda x: "Oui" if x.pack else "Non",
            "A réglé sa cotisation": lambda x: "Oui" if x.account is not None else "Non",
            "Référence adhésion": lambda x: x.pk
        }

        writer = csv.writer(response)
        writer.writerow([field for field in fields.keys()])
        for registration in self.session.registrations.filter(rgpd_sharing_alumni=True).order_by("last_name"):
            writer.writerow([field_processing(registration) for field_processing in fields.values()])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'session': self.session,
            'rgpd_agreement_alumni': RGPD_AGREEMENT_ALUMNI
        })
        return context
