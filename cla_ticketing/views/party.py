import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.http import HttpRequest, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, resolve_url, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View, CreateView, TemplateView, FormView

from cla_auth.mixins import IsContributorMixin
from cla_ticketing.mixins.party import DancingPartyRegistrationMixin, DancingPartyCollegeMixin
from cla_ticketing.models import DancingParty, DancingPartyRegistration, DancingPartyRegistrationCustomField, DancingPartyRegistrationCustomFieldValue
from cla_ticketing.forms.party import ContributorRegistrationForm, NonContributorRegistrationForm, RegistrationEditForm, RegistrationValidationForm


class DancingPartyView(IsContributorMixin, DancingPartyCollegeMixin, DancingPartyRegistrationMixin, TemplateView):
    template_name = "cla_ticketing/party/view_party.html"


class AbstractRegistrationCreateView(IsContributorMixin, DancingPartyCollegeMixin, DancingPartyRegistrationMixin, CreateView):
    is_contributor = False
    dancing_party_college_redirect = True
    model = DancingPartyRegistration

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if self.is_contributor and self.registration_self is not None:
            return redirect("cla_ticketing:party_view", self.party.slug)
        if not self.is_contributor and self.registration_friend is not None:
            return redirect("cla_ticketing:party_view", self.party.slug)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.party.are_registrations_opened:
            return redirect("cla_ticketing:party_view", self.party.slug)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.party.are_registrations_opened:
            return render(request, "cla_ticketing/party/register_failed.html", {'party': self.party, 'message': "La dernière place vient d'être vendue..."})
        return super().post(request, *args, **kwargs)

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

        try:
            # Lock registration table to ensure no registration overshoot the limit
            DancingPartyRegistration.objects.lock()

            if self.party.are_registrations_opened:
                registration.save()

        finally:
            DancingPartyRegistration.objects.unlock()

        # If the registration was not added, redirect to `party_view`
        if not registration.pk:
            return render(self.request, "cla_ticketing/party/register_failed.html", {'party': self.party, 'message': "La dernière place vient d'être vendue..."})

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

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not self.party.allow_non_contributor_registration:
            return redirect("cla_ticketing:party_view", self.party.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return resolve_url("cla_ticketing:party_detail_noncontributor", self.party.slug)


class AbstractRegistrationDetailView(IsContributorMixin, DancingPartyRegistrationMixin, TemplateView):
    registration: DancingPartyRegistration = None

    def get_registration(self):
        pass

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.registration = self.get_registration()
            if self.registration is None:
                raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'registration': self.registration,
            'back_href': self.get_back_href()
        })
        return context

    def get_back_href(self):
        if self.request.GET.get('redirect') == "lobby":
            return resolve_url("cla_member:ticketing")
        return resolve_url("cla_ticketing:party_view", self.party.slug)


class ContributorRegistrationDetailView(AbstractRegistrationDetailView):
    template_name = "cla_ticketing/party/view_registration_contributor.html"

    def get_registration(self):
        return self.party.registrations.filter(user=self.request.user).first()


class NonContributorRegistrationDetailView(AbstractRegistrationDetailView):
    template_name = "cla_ticketing/party/view_registration_noncontributor.html"

    def get_registration(self):
        return self.party.registrations.filter(guarantor=self.request.user).first()


class AbstractRegistrationChangeView(IsContributorMixin, DancingPartyRegistrationMixin, FormView):
    registration: DancingPartyRegistration = None
    template_name = "cla_ticketing/party/change_registration.html"
    form_class = RegistrationEditForm

    def get_registration(self):
        pass

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if not self.party.has_editable_fields or self.party.has_started:
            raise PermissionDenied()
        self.registration = self.get_registration()
        if self.registration is None:
            raise Http404()
        if self.registration.validated:
            raise PermissionDenied()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'registration': self.registration,
            'back_href': self.get_back_href()
        })
        return context

    def get_back_href(self):
        if self.registration.user_id is not None:
            return resolve_url("cla_ticketing:party_detail_contributor", self.party.slug)
        return resolve_url("cla_ticketing:party_detail_noncontributor", self.party.slug)

    def get_initial(self):
        initial = super().get_initial()
        for custom_field in self.party.custom_fields.all():
            try:
                cf_value = DancingPartyRegistrationCustomFieldValue.objects.get(registration=self.registration, field=custom_field)
                if custom_field.type == custom_field.Type.FILE:
                    if cf_value.file_value and cf_value.file_value.url:
                        initial[custom_field.field_id] = cf_value.value
                else:
                    initial[custom_field.field_id] = cf_value.value
            except DancingPartyRegistrationCustomFieldValue.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):

        # Deal with custom fields
        for custom_field in self.party.custom_fields.all():
            if custom_field.type == DancingPartyRegistrationCustomField.Type.TEXT:
                DancingPartyRegistrationCustomFieldValue.objects.get_or_create_text(
                    registration=self.registration, field=custom_field, value=form.cleaned_data[custom_field.field_id]
                )
            elif custom_field.type == DancingPartyRegistrationCustomField.Type.SELECT:
                DancingPartyRegistrationCustomFieldValue.objects.get_or_create_text(
                    registration=self.registration, field=custom_field, value=form.cleaned_data[custom_field.field_id]
                )
            elif custom_field.type == DancingPartyRegistrationCustomField.Type.CHECKBOX:
                DancingPartyRegistrationCustomFieldValue.objects.get_or_create_boolean(
                    registration=self.registration, field=custom_field, value=form.cleaned_data[custom_field.field_id]
                )
            elif custom_field.type == DancingPartyRegistrationCustomField.Type.FILE:
                if form.cleaned_data[custom_field.field_id] is not None:
                    DancingPartyRegistrationCustomFieldValue.objects.get_or_create_file(
                        registration=self.registration, field=custom_field, value=None if not form.cleaned_data[custom_field.field_id] else form.cleaned_data[custom_field.field_id]
                    )

        messages.success(self.request, "Les changements ont bien été sauvegardés")
        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'party': self.party
        })
        return kwargs

    def get_success_url(self):
        return self.get_back_href()


class ContributorRegistrationChangeView(AbstractRegistrationChangeView):
    def get_registration(self):
        return self.party.registrations.filter(user=self.request.user).first()


class NonContributorRegistrationChangeView(AbstractRegistrationChangeView):
    def get_registration(self):
        return self.party.registrations.filter(guarantor=self.request.user).first()


class ValidateRegistrationView(UserPassesTestMixin, LoginRequiredMixin, FormView):
    party: DancingParty = None
    registrations = None
    registration: DancingPartyRegistration = None
    template_name = "cla_ticketing/party/validate_registration.html"
    form_class = RegistrationValidationForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.party = get_object_or_404(DancingParty, slug=kwargs.pop("party_slug"))

    def get_next_registration(self, exclude_self=False):
        registrations = self.party.registrations.filter(Q(validated=False) | Q(paid=False), is_staff=False, debug=False)
        if self.registration:
            registrations = registrations.filter(created_on__gte=self.registration.created_on)
            if exclude_self:
                registrations = registrations.exclude(pk=self.registration.pk)
        return registrations.order_by("created_on").first()

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.dancingparty_manager"):
            return True
        return self.registration.dancing_party.managers.filter(pk=self.request.user.pk).count() > 0

    def get(self, request, *args, **kwargs):
        # Get the registration passed as a parameter
        if self.request.GET.get('registration_pk'):
            self.registration = self.party.registrations.filter(Q(validated=False) | Q(paid=False), pk=self.request.GET.get('registration_pk')).first()

        if self.registration is None:
            self.registration = self.get_next_registration()
        return super(ValidateRegistrationView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.registration = self.party.registrations.filter(pk=self.request.POST.get('registration_pk')).first()
        if self.registration is None:
            messages.warning(request, "L'inscription à laquelle vous souhaitiez accéder n'existe plus")
            return redirect("cla_ticketing:party_validate", self.party.slug)

        return super(ValidateRegistrationView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.registration.paid = form.cleaned_data['paid']
        self.registration.validated = form.cleaned_data['validated']
        self.registration.save()

        if self.registration.validated:
            # Clear files
            for cs in self.registration.custom_fields.filter(field__type=DancingPartyRegistrationCustomField.Type.FILE):
                if cs.field.delete_file_after_validation:
                    if cs.value is not None and cs.value.name:
                        cs.value.delete()

            # Log the validation
            ct = ContentType.objects.get_for_model(self.registration)
            LogEntry.objects.log_action(
                user_id=self.request.user.id,
                content_type_id=ct.pk,
                object_id=self.registration.pk,
                object_repr=str(self.registration),
                action_flag=CHANGE,
                change_message=f"Registration was validated")

        return super().form_valid(form)

    def get_inline_custom_fields(self):
        return [
            (
                cs,
                self.registration.custom_fields.filter(field=cs).first()
            ) for cs in self.party.custom_fields.filter(type__in=DancingPartyRegistrationCustomField.Type.get_inlines_types())
        ] if self.registration else []

    def get_block_custom_fields(self):
        return [
            (
                cs,
                self.registration.custom_fields.filter(field=cs).first()
            ) for cs in self.party.custom_fields.filter(type__in=DancingPartyRegistrationCustomField.Type.get_block_types())
        ] if self.registration else []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'party': self.party,
            'registration': self.registration,
            'inline_custom_fields': self.get_inline_custom_fields(),
            'block_custom_fields': self.get_block_custom_fields(),
            'loop': self.request.GET.get('loop')
        })
        return context

    def get_initial(self):
        return {
            'paid': self.registration.paid,
            'validated': self.registration.validated
        } if self.registration else {}

    def get_success_url(self):
        url = resolve_url("cla_ticketing:party_validate", self.party.slug)
        next_registration = self.get_next_registration(exclude_self=True)
        if next_registration:
            url += f"?registration_pk={next_registration.pk}"
        else:
            url += f"?loop=1"
        return url


class CheckInPartyView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    party: DancingParty = None
    template_name = "cla_ticketing/party/checkin_party.html"

    def setup(self, request, *args, **kwargs):
        self.party = get_object_or_404(DancingParty, slug=kwargs.pop("party_slug"))
        super().setup(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.dancingparty_manager"):
            return True
        elif self.party.managers.filter(pk=self.request.user.pk).count() > 0:
            return True
        return self.party.scanners.filter(pk=self.request.user.pk).count() > 0

    def post(self, request: HttpRequest, *args, **kwargs):
        search_value = request.POST.get('search_value')
        results = []
        if len(search_value) > 0:
            results = [
                {
                    'pk': r.pk,
                    'first_name': r.first_name,
                    'last_name': r.last_name,
                    'ticket_label': r.ticket_label,
                    'checked_in': r.checkin_datetime is not None,
                    'is_contributor': r.user is not None,
                    'href': resolve_url("cla_ticketing:party_checkin_registration", self.party.slug, r.pk),
                } for r in self.party.registrations
                               .annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
                               .filter(
                    Q(first_name__icontains=search_value) |
                    Q(last_name__icontains=search_value) |
                    Q(fullname__icontains=search_value)
                ).order_by("last_name")[:5]
            ]
        return JsonResponse({
            'success': True,
            'payload': results
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'party': self.party,
            'is_manager': self.request.user.has_perm("cla_ticketing.dancingparty_manager") or self.party.managers.filter(pk=self.request.user.pk).count() > 0
        })
        return context


class CheckInQRCodeView(UserPassesTestMixin, LoginRequiredMixin, View):
    party: DancingParty = None

    def setup(self, request, *args, **kwargs):
        self.party = get_object_or_404(DancingParty, slug=kwargs.pop("party_slug"))
        super().setup(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.dancingparty_manager"):
            return True
        elif self.party.managers.filter(pk=self.request.user.pk).count() > 0:
            return True
        return self.party.scanners.filter(pk=self.request.user.pk).count() > 0

    def get(self, request: HttpRequest, *args, **kwargs):
        try:
            payload = jwt.decode(
                jwt=kwargs.pop("token"),
                key=settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.DecodeError:
            return JsonResponse({
                'success': False,
                'message': "Invalid token"
            }, status=400)

        try:
            r = DancingPartyRegistration.objects.get(pk=payload.get('pk', None), dancing_party=self.party)
            return JsonResponse({
                'success': True,
                'href': resolve_url("cla_ticketing:party_checkin_registration", self.party.slug, r.pk)
            })
        except DancingPartyRegistration.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': "No matched"
            }, status=404)


class CheckInRegistrationView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    registration: DancingPartyRegistration = None
    template_name = "cla_ticketing/party/checkin_registration.html"

    def setup(self, request, *args, **kwargs):
        self.registration = get_object_or_404(DancingPartyRegistration, pk=kwargs.pop("registration_pk"), dancing_party__slug=kwargs.pop("party_slug"))
        super().setup(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.has_perm("cla_ticketing.dancingparty_manager"):
            return True
        elif self.registration.dancing_party.managers.filter(pk=self.request.user.pk).count() > 0:
            return True
        return self.registration.dancing_party.scanners.filter(pk=self.request.user.pk).count() > 0

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.registration.checkin_datetime is None:
            self.registration.checkin_datetime = timezone.now()
            self.registration.save()

            ct = ContentType.objects.get_for_model(self.registration)
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ct.pk,
                object_id=self.registration.pk,
                object_repr=str(self.registration),
                action_flag=CHANGE,
                change_message=f"Registration was checked in")

        return redirect("cla_ticketing:party_checkin", self.registration.dancing_party.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'party': self.registration.dancing_party,
            'is_manager': self.request.user.has_perm("cla_ticketing.dancingparty_manager") or self.registration.dancing_party.managers.filter(pk=self.request.user.pk).count() > 0,
            'registration': self.registration
        })
        return context
