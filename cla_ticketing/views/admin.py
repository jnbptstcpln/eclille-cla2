import csv
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse


from cla_ticketing.models import Event


class EventRegistrationExportView(UserPassesTestMixin, generic.View):

    event: Event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs.pop("event_pk", None))
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.add_event"):
            return True
        elif self.request.user.has_perm("cla_ticketing.event_manager"):
            return self.event.managers.filter(pk=self.request.user.pk).count() > 0
        return False

    def get(self, req: HttpRequest):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="' + str(self.event.name) + '.csv"'},
        )

        fields = {
            "Nom": lambda x: x.last_name,
            "Prénom": lambda x: x.first_name,
            "Adresse mail": lambda x: x.email,
            "Numéro de téléphone": lambda x: x.phone,
            "Date inscription": lambda x: x.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            "Type de place": lambda x: str(x.type.name),
            "Prix de la place": lambda x: str(x.type.price),
            "Statut de l'étudiant": lambda x: x.get_student_status_display(),
            "A payé": lambda x: "Oui" if x.paid else "Non"
        }

        writer = csv.writer(response)
        writer.writerow([field for field in fields.keys()])
        for registration in self.event.registrations.order_by("last_name"):
            writer.writerow([field_processing(registration) for field_processing in fields.values()])

        return response
