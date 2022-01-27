from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.template.loader import render_to_string
from django.views.generic import CreateView, DetailView
from cla_registration.models import RegistrationSession, Registration
from cla_registration.forms import RegistrationForm, RegistrationPackForm, EnsclRegistrationForm


def register_introduction(req):
    return render(
        req,
        "cla_registration/registration/introduction.html",
        {
            'page_active': "registration"
        }
    )


class AbstractRegistrationView(CreateView):
    is_from_another_school = False
    current_registration_session = None
    model = Registration
    form_class = RegistrationForm
    pack = False
    contribution = None
    school_domain = None
    registration_type = None
    template_name = "cla_registration/registration/register.html"
    ticketing_field = ""
    registration: Registration = None
    description = None
    send_email_notification = False

    def dispatch(self, request, *args, **kwargs):
        self.current_registration_session = RegistrationSession.objects.get_current_registration_session()
        if self.current_registration_session is None:
            return render(request, "cla_registration/registration/registration_closed.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.registration = form.save(False)
        if self.current_registration_session.registrations.filter(email_school=self.registration.email_school).count() == 0:
            self.registration.session = self.current_registration_session
            self.registration.type = self.registration_type
            self.registration.school = self.school_domain
            self.registration.contribution = self.contribution
            self.registration.pack = self.pack
            if self.is_from_another_school:
                self.registration.original_school = form.cleaned_data.get('original_school')
            self.registration.save()
        else:
            self.registration = self.current_registration_session.registrations.filter(email_school=self.registration.email_school).first()

        self.registration.save()

        if self.send_email_notification:
            try:
                send_mail(
                    subject=f"[Nouvelle Adhésion] {self.registration.get_school_display()} {self.registration.first_name.upper()} {self.registration.last_name}",
                    from_email=settings.EMAIL_HOST_FROM,
                    recipient_list=[settings.EMAIL_HOST_FROM],
                    message=f"Une demande d'adhésion vient d'être effectué sur le site pour l'étudiant {self.registration.first_name} {self.registration.last_name}",
                    html_message=render_to_string(
                        'cla_registration/admin/mail.html',
                        {
                            'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                            'campaign_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('admin:cla_registration_registrationsession_change', self.current_registration_session.pk)}",
                            'registration': self.registration
                        }
                    )
                )
            except Exception as e:
                pass

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'school_domain': self.school_domain,
            'is_from_another_school': self.is_from_another_school
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'description': self.description,
            'back_href': self.get_back_url()
        })
        return context

    def get_success_url(self):
        return resolve_url("cla_registration:register_paiement", self.registration.pk)

    def get_back_url(self):
        return resolve_url("cla_registration:register_introduction")

    def on_registration_created(self):
        pass


class AbstractPackRegistrationView(AbstractRegistrationView):
    form_class = RegistrationPackForm
    pack = True


class CentralePackRegistrationView(AbstractPackRegistrationView):
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_PACK
    contribution = 355
    description = "Étudiante ou étudiant à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations et à Centrale Lille Alumni en profitant du pack CLA+Alumni."
    send_email_notification = True


class CentralePackDDRegistrationView(AbstractPackRegistrationView):
    is_from_another_school = True
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_DD_PACK
    contribution = 265
    description = "Étudiante ou étudiant en double diplôme à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations et à Centrale Lille Alumni en profitant du pack CLA+Alumni."
    send_email_notification = True


class ITEEMPackRegistrationView(AbstractPackRegistrationView):
    school_domain = Registration.SchoolDomains.ITEEM
    registration_type = Registration.Types.ITEEM_PACK
    contribution = 445
    description = "Étudiante ou étudiant à l'ITEEM, vous souhaitez adhérer à Centrale Lille Associations et à Centrale Lille Alumni en profitant du pack CLA+Alumni."
    send_email_notification = True


class CentraleCLARegistrationView(AbstractRegistrationView):
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_CLA
    contribution = 270
    description = "Étudiante ou étudiant à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations."
    send_email_notification = True


class CentraleCLADDRegistrationView(AbstractRegistrationView):
    is_from_another_school = True
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_DD_CLA
    contribution = 180
    description = "Étudiante ou étudiant en double diplôme à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations."
    send_email_notification = True


class ITEEMCLARegistrationView(AbstractRegistrationView):
    school_domain = Registration.SchoolDomains.ITEEM
    registration_type = Registration.Types.ITEEM_CLA
    contribution = 360
    description = "Étudiante ou étudiant à l'ITEEM, vous souhaitez adhérer à Centrale Lille Associations."
    send_email_notification = True


class ENSCLCLARegistrationView(AbstractRegistrationView):
    form_class = EnsclRegistrationForm
    school_domain = Registration.SchoolDomains.ENSCL
    registration_type = Registration.Types.ENSCL_CLA
    contribution = 265
    description = "Étudiante ou étudiant à l'ENSCL, vous souhaitez adhérer à Centrale Lille Associations."
    send_email_notification = True


class RegistrationPaiementView(DetailView):
    model = Registration
    template_name = "cla_registration/registration/registration_paiement.html"


class RegistrationPaiementCheckView(DetailView):
    model = Registration
    template_name = "cla_registration/registration/registration_paiement_check.html"
