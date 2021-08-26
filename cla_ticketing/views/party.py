from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.utils.decorators import method_decorator
from django.views.generic import View, CreateView, TemplateView

from cla_auth.mixins import IsContributorMixin
from cla_ticketing.mixins.party import DancingPartyRegistrationMixin
from cla_ticketing.models import DancingParty, DancingPartyRegistration, DancingPartyRegistrationCustomField, DancingPartyRegistrationCustomFieldValue
from cla_ticketing.forms.party import ContributorRegistrationForm, NonContributorRegistrationForm


class DancingPartyView(DancingPartyRegistrationMixin, IsContributorMixin, TemplateView):
    template_name = "cla_ticketing/party/view_party.html"


class AbstractRegistrationCreateView(DancingPartyRegistrationMixin, IsContributorMixin, CreateView):
    is_contributor = False
    model = DancingPartyRegistration

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not self.party.are_registrations_opened:
            return redirect("cla_ticketing:party_view", self.party.slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        registration: DancingPartyRegistration = form.save(commit=False)
        registration.dancing_party = self.party
        if self.is_contributor:
            registration.student_status = DancingPartyRegistration.StudentStatus.CONTRIBUTOR
            registration.user = self.request.user
            registration.first_name = registration.user.first_name
            registration.last_name = registration.user.last_name
            registration.email = registration.user.email
            registration.phone = registration.user.infos.phone
            registration.birthdate = registration.user.infos.birthdate
        else:
            registration.student_status = DancingPartyRegistration.StudentStatus.NON_CONTRIBUTOR
            registration.guarantor = self.request.user
        registration.save()

        # Deal with custom fields
        for custom_field in self.party.custom_fields.all():
            if custom_field.type == DancingPartyRegistrationCustomField.Type.TEXT:
                DancingPartyRegistrationCustomFieldValue.objects.get_or_create_text(
                    registration=registration, field=custom_field, value=form.cleaned_data[custom_field.field_id]
                )
            elif custom_field.type == DancingPartyRegistrationCustomField.Type.SELECT:
                DancingPartyRegistrationCustomFieldValue.objects.get_or_create_text(
                    registration=registration, field=custom_field, value=form.cleaned_data[custom_field.field_id]
                )
            elif custom_field.type == DancingPartyRegistrationCustomField.Type.CHECKBOX:
                DancingPartyRegistrationCustomFieldValue.objects.get_or_create_boolean(
                    registration=registration, field=custom_field, value=form.cleaned_data[custom_field.field_id]
                )
            elif custom_field.type == DancingPartyRegistrationCustomField.Type.FILE:
                if form.cleaned_data[custom_field.field_id] is not None:
                    DancingPartyRegistrationCustomFieldValue.objects.get_or_create_file(
                        registration=registration, field=custom_field, value=None if not form.cleaned_data[custom_field.field_id] else form.cleaned_data[custom_field.field_id]
                    )

        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'party': self.party
        })
        return kwargs


class ContributorRegistrationCreateView(AbstractRegistrationCreateView):
    is_contributor = True
    template_name = "cla_ticketing/party/register_contributor.html"
    form_class = ContributorRegistrationForm

    def get_success_url(self):
        return resolve_url("cla_ticketing:party_detail_contributor", self.party.slug)


class NonContributorRegistrationCreateView(AbstractRegistrationCreateView):
    is_contributor = False
    template_name = "cla_ticketing/party/register_noncontributor.html"
    form_class = NonContributorRegistrationForm

    def get_success_url(self):
        return resolve_url("cla_ticketing:party_detail_noncontributor", self.party.slug)


class AbstractRegistrationDetailView(DancingPartyRegistrationMixin, IsContributorMixin, TemplateView):
    registration: DancingPartyRegistration = None

    def get_registration(self):
        pass

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.registration = self.get_registration()
        if self.registration is None:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'registration': self.registration
        })
        return context


class ContributorRegistrationDetailView(AbstractRegistrationDetailView):
    template_name = "cla_ticketing/party/view_registration_contributor.html"

    def get_registration(self):
        return self.party.registrations.filter(user=self.request.user).first()


class NonContributorRegistrationDetailView(AbstractRegistrationDetailView):
    template_name = "cla_ticketing/party/view_registration_noncontributor.html"

    def get_registration(self):
        return self.party.registrations.filter(guarantor=self.request.user).first()
