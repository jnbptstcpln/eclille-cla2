from django import forms
from django.core.exceptions import ValidationError

from cla_ticketing.fields import CustomFileInput
from cla_ticketing.models import DancingParty, DancingPartyRegistration
from cla_registration.utils import capitalize_name


class AbstractRegistrationForm(forms.ModelForm):
    party: DancingParty = None

    class Meta:
        model = DancingPartyRegistration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.party = kwargs.pop("party")
        super().__init__(*args, **kwargs)

        for cs in self.party.custom_fields.filter(admin_only=False):
            self.fields[cs.field_id] = cs.get_field_instance()

        # Customising all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control form-control-sm"


class ContributorRegistrationForm(AbstractRegistrationForm):

    class Meta(AbstractRegistrationForm.Meta):
        fields = 'type', 'home'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['type'].choices = (
            (DancingPartyRegistration.Types.HARD.value, f"{DancingPartyRegistration.Types.HARD.label} - 6€"),
            (DancingPartyRegistration.Types.SOFT.value, f"{DancingPartyRegistration.Types.SOFT.label} - 4€")
        )


class NonContributorRegistrationForm(AbstractRegistrationForm):

    class Meta(AbstractRegistrationForm.Meta):
        fields = 'first_name', 'last_name', 'email', 'birthdate', 'phone', 'type', 'home'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['type'].choices = (
            (DancingPartyRegistration.Types.HARD.value, f"{DancingPartyRegistration.Types.HARD.label} - 10€"),
            (DancingPartyRegistration.Types.SOFT.value, f"{DancingPartyRegistration.Types.SOFT.label} - 8€")
        )

    def clean_first_name(self):
        return capitalize_name(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return capitalize_name(self.cleaned_data['last_name'])


class RegistrationEditForm(forms.Form):
    party: DancingParty = None

    def __init__(self, *args, **kwargs):
        self.party = kwargs.pop("party")
        super().__init__(*args, **kwargs)

        for cs in self.party.custom_fields.filter(admin_only=False):
            self.fields[cs.field_id] = cs.get_field_instance()
            # Custom handling for FileInput
            if cs.type == cs.Type.FILE:
                # If a value was already provided, the input is not longer required
                if self.initial.get(cs.field_id) is not None and hasattr(self.initial[cs.field_id], 'url'):
                    self.fields[cs.field_id].required = False
                self.fields[cs.field_id].widget = CustomFileInput()

        # Customising all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control form-control-sm"


class RegistrationValidationForm(forms.Form):

    paid = forms.BooleanField(
        required=False,
        label="Place payée"
    )
    validated = forms.BooleanField(
        required=False,
        label="Place validée"
    )
