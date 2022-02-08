import csv
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.models import LogEntry, CHANGE

from cla_ticketing.models import Event, EventRegistration, DancingPartyRegistration, DancingParty


@method_decorator(csrf_exempt, name='dispatch')
class EventRegistrationTogglePaidView(UserPassesTestMixin, generic.View):
    registration: EventRegistration = None

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.add_event"):
            return True
        elif self.request.user.has_perm("cla_ticketing.event_manager"):
            return self.registration.event.managers.filter(pk=self.request.user.pk).count() > 0
        return False

    def dispatch(self, request, *args, **kwargs):
        self.registration = get_object_or_404(EventRegistration, pk=kwargs.pop("pk", None), event_id=kwargs.pop("event_pk", None))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.registration.paid = not self.registration.paid
        self.registration.save()
        ct = ContentType.objects.get_for_model(self.registration)
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ct.pk,
            object_id=self.registration.pk,
            object_repr=str(self.registration),
            action_flag=CHANGE,
            change_message=f"Registration set to PAID={str(self.registration.paid)}")
        return JsonResponse({'paid': self.registration.paid})


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


@method_decorator(csrf_exempt, name='dispatch')
class DancingPartyRegistrationTogglePaidView(UserPassesTestMixin, generic.View):
    registration: DancingPartyRegistration = None

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.add_dancingparty"):
            return True
        elif self.request.user.has_perm("cla_ticketing.dancingparty_manager"):
            return self.registration.dancing_party.managers.filter(pk=self.request.user.pk).count() > 0
        return False

    def dispatch(self, request, *args, **kwargs):
        self.registration = get_object_or_404(DancingPartyRegistration, pk=kwargs.pop("pk", None), dancing_party_id=kwargs.pop("party_pk", None))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.registration.paid = not self.registration.paid
        self.registration.save()
        ct = ContentType.objects.get_for_model(self.registration)
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ct.pk,
            object_id=self.registration.pk,
            object_repr=str(self.registration),
            action_flag=CHANGE,
            change_message=f"Registration set to PAID={str(self.registration.paid)}")
        return JsonResponse({'paid': self.registration.paid})


class DancingPartyExportView(UserPassesTestMixin, generic.View):

    party: DancingParty = None

    def dispatch(self, request, *args, **kwargs):
        self.party = get_object_or_404(DancingParty, pk=kwargs.pop("party_pk", None))
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.add_dancingparty"):
            return True
        elif self.request.user.has_perm("cla_ticketing.dancingparty_manager"):
            return self.party.managers.filter(pk=self.request.user.pk).count() > 0
        return False

    def get(self, req: HttpRequest):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="' + str(self.party.name) + '.csv"'},
        )

        def get_cursus(x: DancingPartyRegistration):
            if x.user and hasattr(x.user, 'infos'):
                return x.user.infos.cursus
            elif x.guarantor and hasattr(x.guarantor, 'infos'):
                return x.guarantor.infos.cursus
            else:
                return "Non précisé"

        fields = {
            "Nom": lambda x: x.last_name,
            "Prénom": lambda x: x.first_name,
            "Adresse mail": lambda x: x.email,
            "Numéro de téléphone": lambda x: x.phone,
            "Date de naissance": lambda x: x.birthdate.strftime("%Y-%m-%d"),
            "Cursus": get_cursus,
            "Logement en fin de soirée": lambda x: x.home,
            "Date inscription": lambda x: x.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            "Type de place": lambda x: f"{x.get_student_status_display()} {x.get_type_display().lower()}" if not x.is_staff else f"Staff : {x.staff_description}",
            "Prix de la place": lambda x: str(x.price) if x.type is not None else 0,
            "A payé": lambda x: "Oui" if x.paid else "Non",
            "Moyen de paiement": lambda x: x.get_mean_of_paiement_display() if x.mean_of_paiement is not None else "Non précisé",
            "Date et heure d'entrée": lambda x: x.checkin_datetime.strftime("%Y-%m-%d %H:%M:%S") if x.checkin_datetime is not None else "Non enregistré"
        }

        writer = csv.writer(response)
        writer.writerow([field for field in fields.keys()])
        for registration in self.party.registrations.filter(debug=False).order_by("last_name"):
            writer.writerow([field_processing(registration) for field_processing in fields.values()])

        return response
