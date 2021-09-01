from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView
from cla_registration.models import RegistrationSession, Registration
from cla_registration.forms import RegistrationForm, RegistrationPackForm


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
    description = None

    def dispatch(self, request, *args, **kwargs):
        self.current_registration_session = RegistrationSession.objects.get_current_registration_session()
        if self.current_registration_session is None:
            return render(request, "cla_registration/registration/registration_closed.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        registration = form.save(False)
        if self.current_registration_session.registrations.filter(email_school=registration.email_school).count() == 0:
            registration.session = self.current_registration_session
            registration.type = self.registration_type
            registration.school = self.school_domain
            registration.contribution = self.contribution
            registration.pack = self.pack
            if self.is_from_another_school:
                registration.original_school = form.cleaned_data.get('original_school')
            registration.save()
        else:
            registration = self.current_registration_session.registrations.filter(email_school=registration.email_school).first()

        return redirect("cla_registration:register_paiement", registration.pk)

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
            'description': self.description
        })
        return context


class AbstractPackRegistrationView(AbstractRegistrationView):
    form_class = RegistrationPackForm
    pack = True


class CentralePackRegistrationView(AbstractPackRegistrationView):
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_PACK
    contribution = 355
    description = "Étudiante ou étudiant à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations et à Centrale Lille Alumni en profitant du pack CLA+Alumni."


class CentralePackDDRegistrationView(AbstractPackRegistrationView):
    is_from_another_school = True
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_DD_PACK
    contribution = 265
    description = "Étudiante ou étudiant en double diplôme à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations et à Centrale Lille Alumni en profitant du pack CLA+Alumni."


class ITEEMPackRegistrationView(AbstractPackRegistrationView):
    school_domain = Registration.SchoolDomains.ITEEM
    registration_type = Registration.Types.ITEEM_PACK
    contribution = 445
    description = "Étudiante ou étudiant à l'ITEEM, vous souhaitez adhérer à Centrale Lille Associations et à Centrale Lille Alumni en profitant du pack CLA+Alumni."


class CentraleCLARegistrationView(AbstractRegistrationView):
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_CLA
    contribution = 270
    description = "Étudiante ou étudiant à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations."


class CentraleCLADDRegistrationView(AbstractRegistrationView):
    is_from_another_school = True
    school_domain = Registration.SchoolDomains.CENTRALE
    registration_type = Registration.Types.CENTRALE_DD_CLA
    contribution = 180
    description = "Étudiante ou étudiant en double diplôme à l'école Centrale de Lille, vous souhaitez adhérer à Centrale Lille Associations."


class ITEEMCLARegistrationView(AbstractRegistrationView):
    school_domain = Registration.SchoolDomains.ITEEM
    registration_type = Registration.Types.ITEEM_CLA
    contribution = 360
    description = "Étudiante ou étudiant à l'ITEEM, vous souhaitez adhérer à Centrale Lille Associations."


class RegistrationPaiementView(DetailView):
    model = Registration
    template_name = "cla_registration/registration/registration_paiement.html"


class RegistrationPaiementCheckView(DetailView):
    model = Registration
    template_name = "cla_registration/registration/registration_paiement_check.html"
