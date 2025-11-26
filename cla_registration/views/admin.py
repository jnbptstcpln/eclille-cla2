import csv
import bugsnag

from django.template.loader import render_to_string
from django.views import generic
from django.contrib import admin, messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponseNotAllowed, Http404, HttpResponse
from django.utils import timezone
from django_weasyprint import WeasyTemplateResponseMixin
from weasyprint import HTML

from cla_association.models import Association, AssociationMember
from cla_auth.utils import create_username
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
        self.registration = get_object_or_404(
            Registration,
            pk=kwargs.pop("registration_pk", None),
            session__pk=kwargs.pop("session_pk", None),
        )
        # Raise 404 error if the registration has already been linked to an account
        if self.registration.account is not None:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            # Update the registration
            self.registration.first_name = form.cleaned_data["first_name"]
            self.registration.last_name = form.cleaned_data["last_name"]
            self.registration.email = form.cleaned_data["email"]
            self.registration.email_school = form.cleaned_data["email_school"]
            self.registration.birthdate = form.cleaned_data["birthdate"]
            self.registration.contribution = form.cleaned_data["amount"]
            self.registration.original_school = form.cleaned_data.get(
                "original_school", None
            )
            # If the student finally change his mind about taking the pack
            if self.registration.is_pack_available:
                self.registration.pack = int(form.cleaned_data["pack"])
                self.registration.type = f'{self.registration.type_prefix}_{"pack" if self.registration.pack else "cla"}'
                if self.registration.pack:
                    self.registration.rgpd_sharing_alumni = True
        except Exception as e:
            bugsnag.notify(e, metadata={"form": form.cleaned_data})

        # Creating user object
        user = User(
            username=create_username(
                form.cleaned_data["first_name"], form.cleaned_data["last_name"]
            ),
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
        )
        user.save()

        # Creating associated information
        user_infos = UserInfos(
            user=user,
            email_school=form.cleaned_data["email_school"],
            birthdate=form.cleaned_data["birthdate"],
            promo=form.cleaned_data["promo"],
            cursus=form.cleaned_data["cursus"],
            phone=form.cleaned_data["phone"],
            original_school=form.cleaned_data.get("original_school", None),
        )
        user_infos.save()

        # Creating associated membership
        membership = UserMembership(
            user=user,
            amount=form.cleaned_data["amount"],
            paid_on=form.cleaned_data["paid_on"],
            paid_by=form.cleaned_data["paid_by"],
            paid_validated=form.cleaned_data["paid_validated"],
            payment_installments=form.cleaned_data["payment_installments"],
            payment_months=form.cleaned_data["payment_months"],
            alumni_pack=form.cleaned_data.get("pack") == 1,
        )
        membership.save()

        self.registration.account = user
        self.registration.save()

        messages.success(
            self.request,
            f"L'utilisateur a été créé et un mail de bienvenue lui a été envoyé à {user.infos.email_school} avec un lien d'activation",
        )
        return redirect(
            "admin:cla_registration_registrationsession_change",
            self.registration.session.pk,
        )
        # return redirect("admin:auth_user_change", user.pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "is_from_another_school": self.registration.original_school is not None,
                "is_pack_available": self.registration.is_pack_available,
            }
        )
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
        elif self.registration.school == Registration.SchoolDomains.ENSCL:
            cursus = UserInfos.CursusChoices.CH1
            promo = self.registration.session.school_year + 3

        return {
            "pack": 1 if self.registration.pack else 0,
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
            "paid_by": None,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "opts": RegistrationSession._meta,
                "original": self.registration,
                "title": "Nouvel utilisateur",
                "site_header": admin.site.site_header,
                "site_title": admin.site.site_title,
            }
        )
        return context


class RegistrationSessionExportView(UserPassesTestMixin, generic.View):

    def test_func(self):
        return self.request.user.has_perm("cla_registration.change_registrationsession")

    def get(self, req: HttpRequest, session_pk):
        session = get_object_or_404(RegistrationSession, pk=session_pk)

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=\"Campagne d'adhésion "
                + str(session.school_year)
                + '.csv"'
            },
        )

        def get_mean_of_paiement(x: Registration):
            if x.account is not None:
                if hasattr(x.account, "membership"):
                    output = x.account.membership.get_paid_by_display()
                    output += (
                        f" - {x.account.membership.get_payment_installments_display()}"
                        if x.account.membership.payment_installments is not None
                        else ""
                    )
                    output += (
                        f" {x.account.membership.get_payment_months_display()}"
                        if x.account.membership.payment_months is not None
                        and x.account.membership.payment_months >= 2
                        else ""
                    )
                    return output
                return "Aucune cotisation enregistrée"
            return "N'a pas encore payé"

        def get_paiement_validation(x: Registration):
            if x.account is not None:
                if hasattr(x.account, "membership"):
                    return "Oui" if x.account.membership.paid_validated else "Non"
                return "---"
            return "---"

        fields = {
            "Nom": lambda x: x.last_name,
            "Prénom": lambda x: x.first_name,
            "Adresse mail": lambda x: x.email,
            "Adresse mail école": lambda x: x.email_school,
            "Numéro de téléphone": lambda x: x.phone,
            "Date de naissance": lambda x: x.birthdate.strftime("%Y-%m-%d"),
            "Type": lambda x: x.type,
            "Date inscription": lambda x: x.datetime_registration.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "Ecole": lambda x: x.school,
            "Double diplôme entrant": lambda x: (
                f"Oui ({x.original_school})" if x.original_school is not None else "Non"
            ),
            "Montant de la cotisation": lambda x: f"{x.contribution}€",
            "A choisi le pack": lambda x: "Oui" if x.pack else "Non",
            "A réglé sa cotisation": lambda x: (
                "Oui" if x.account is not None else "Non"
            ),
            "Moyen de paiement": get_mean_of_paiement,
            "Paiement validé": get_paiement_validation,
            "Référence adhésion": lambda x: x.pk,
        }

        writer = csv.writer(response)
        writer.writerow([field for field in fields.keys()])
        for registration in session.registrations.order_by("last_name"):
            writer.writerow(
                [field_processing(registration) for field_processing in fields.values()]
            )

        return response


class MembershipProofView(
    WeasyTemplateResponseMixin, UserPassesTestMixin, generic.DetailView
):
    model = User
    membership: UserMembership = None
    template_name = "cla_registration/admin/membership_pdf.html"

    def test_func(self):
        return self.request.user.has_perm("cla_registration.view_registration")

    def get_context_data(self, **kwargs):

        if not hasattr(self.object, "infos"):
            raise Http404()

        if not self.object.infos.has_active_membership():
            raise Http404()

        self.membership = self.object.infos.get_active_membership()

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "user": self.object,
                "membership": self.membership,
                "treasurer": Association.objects.get_cla()
                .members.filter(_role=AssociationMember.Roles.TREASURER)
                .first(),
                "associations": {"cla": Association.objects.get_cla()},
            }
        )
        return context
