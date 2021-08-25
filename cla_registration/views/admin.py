import csv
from django.views import generic
from django.contrib import admin, messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponseNotAllowed, Http404, HttpResponse
from django.utils import timezone


from cla_registration.models import Registration, RegistrationSession
from cla_registration.forms import RegistrationAdminForm
from cla_auth.models import UserInfos, UserMembership


class RegistrationValidationView(UserPassesTestMixin, generic.FormView):
    registration: Registration = None
    form_class = RegistrationAdminForm
    template_name = "cla_registration/admin/registration_view.html"

    def test_func(self):
        return self.request.user.has_perm("cla_registration.view_registration")

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        # Get the registration
        self.registration = get_object_or_404(Registration, pk=kwargs.pop("registration_pk", None), session__pk=kwargs.pop("session_pk", None))
        # Raise 404 error if the registration has already been linked to an account
        if self.registration.account is not None:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Creating user object
        user = User(
            username=f"{slugify(form.cleaned_data['first_name'])}.{slugify(form.cleaned_data['last_name'])}",
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email']
        )
        user.save()

        # Creating associated informations
        user_infos = UserInfos(
            user=user,
            email_school=form.cleaned_data['email_school'],
            birthdate=form.cleaned_data['birthdate'],
            promo=form.cleaned_data['promo'],
            cursus=form.cleaned_data['cursus'],
            phone=form.cleaned_data['phone'],
            original_school=form.cleaned_data.get('original_school', None)
        )
        user_infos.save()

        # Creating associated membership
        membership = UserMembership(
            user=user,
            amount=form.cleaned_data['amount'],
            paid_on=form.cleaned_data['paid_on'],
            paid_by=form.cleaned_data['paid_by']
        )
        membership.save()

        self.registration.account = user
        self.registration.save()

        messages.success(self.request, f"Un mail de bienvenue a été envoyé à {user.infos.email_school} avec un lien d'activation")
        return redirect("admin:auth_user_change", user.pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'is_from_another_school': self.registration.original_school is not None
        })
        return kwargs

    def get_initial(self):
        cursus = None
        promo = None
        if self.registration.school == Registration.SchoolDomains.CENTRALE:
            if self.registration.type == Registration.Types.CENTRALE_DD_CLA:
                if self.registration.original_school.upper() == "EDHEC":
                    cursus = UserInfos.CursusChoices.G1_DD_EDHEC
                else:
                    cursus = UserInfos.CursusChoices.G1_DD_INTERNATIONAL
            else:
                cursus = UserInfos.CursusChoices.G1
            promo = self.registration.session.school_year + 3
        elif self.registration.school == Registration.SchoolDomains.ITEEM:
            cursus = UserInfos.CursusChoices.IE1
            promo = self.registration.session.school_year + 5

        return {
            "first_name": self.registration.first_name,
            "last_name": self.registration.last_name,
            "email": self.registration.email,
            "email_school": self.registration.email_school,
            "phone": self.registration.phone,
            "birthdate": self.registration.birthdate,
            "cursus": cursus,
            "promo": promo,
            "amount": self.registration.contribution,
            "original_school": self.registration.original_school,
            "paid_on": timezone.now().date(),
            "paid_by": None
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'opts': RegistrationSession._meta,
            'original': self.registration,
            'title': "Nouvel utilisateur",
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title
        })
        return context


class RegistrationSessionExportView(UserPassesTestMixin, generic.View):

    def test_func(self):
        return self.request.user.has_perm("cla_registration.change_registrationsession")

    def get(self, req: HttpRequest, session_pk):
        session = get_object_or_404(RegistrationSession, pk=session_pk)

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="Campagne d\'adhésion ' + str(session.school_year) + '.csv"'},
        )

        fields = {
            "Nom": lambda x: x.last_name,
            "Prénom": lambda x: x.first_name,
            "Adresse mail": lambda x: x.email,
            "Adresse mail école": lambda x: x.email_school,
            "Numéro de téléphone": lambda x: x.phone,
            "Date de naissance": lambda x: x.birthdate.strftime("%Y-%m-%d"),
            "Type": lambda x: x.type,
            "Date inscription": lambda x: x.datetime_registration.strftime("%Y-%m-%d %H:%M"),
            "Ecole": lambda x: x.school,
            "Double diplôme entrant": lambda x: f"Oui ({x.original_school})" if x.original_school is not None else "Non",
            "Montant de la cotisation": lambda x: f"{x.contribution}€",
            "A choisi le pack (a cotisé pour adhérer à Centrale Lille Alumni)": lambda x: "Oui" if x.pack else "Non",
            "A réglé sa cotisation": lambda x: "Oui" if x.account is not None else "Non",
            "Référence adhésion": lambda x: x.pk
        }

        writer = csv.writer(response)
        writer.writerow([field for field in fields.keys()])
        for registration in session.registrations.order_by("last_name"):
            writer.writerow([field_processing(registration) for field_processing in fields.values()])

        return response
