from django import forms
from .models import Registration

from cla_auth.forms.admin_user_form import UserCreationForm
from cla_auth.models import UserInfos, UserMembership
from cla_registration.strings import RGPD_AGREEMENT_CLA, RGPD_AGREEMENT_ALUMNI


class RegistrationForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = [
            'first_name',
            'last_name',
            'email',
            'email_school',
            'phone',
            'birthdate',
            'rgpd_agreement',
            'rgpd_sharing_alumni',
        ]

    def __init__(self, *args, **kwargs):
        self.school_domain = kwargs.pop("school_domain", "centralelille.fr")
        self.is_from_another_school = kwargs.pop("is_from_another_school", False)
        super().__init__(*args, **kwargs)

        if self.is_from_another_school:
            self.fields['original_school'] = forms.CharField(
                max_length=255,
                label="École ou université d'origine"
            )
            self.fields['original_school'].widget.attrs['placeholder'] = "EDHEC, Université de Madrid, ..."
            self.fields['email_school'].label = "Adresse mail centralienne"

        # Setup placeholder
        self.fields['first_name'].widget.attrs['placeholder'] = f"Prénom"
        self.fields['last_name'].widget.attrs['placeholder'] = f"Nom"
        self.fields['birthdate'].widget.attrs['placeholder'] = f"DD/MM/YYYY"
        self.fields['email'].widget.attrs['placeholder'] = f"prenom.nom@example.com"
        self.fields['email_school'].widget.attrs['placeholder'] = f"prenom.nom@{self.school_domain}"
        self.fields['phone'].widget.attrs['placeholder'] = f"+33 6 00 00 00 00"


        for field_name, field in self.fields.items():
            if field_name.startswith('rgpd_'):
                continue
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    rgpd_agreement = forms.BooleanField(
        label=RGPD_AGREEMENT_CLA,
        required=True
    )
    rgpd_sharing_alumni = forms.BooleanField(
        label=RGPD_AGREEMENT_ALUMNI,
        required=False
    )

    def clean_email_school(self):
        email = self.cleaned_data['email']
        email_school = self.cleaned_data['email_school']
        if not email_school.endswith(self.school_domain):
            raise forms.ValidationError(f"Veuillez vérifier que votre adresse mail scolaire finit bien en @{self.school_domain}")
        if email == email_school:
            raise forms.ValidationError('Veuillez indiquer une adresse mail personnelle différente de votre adresse mail fournie par l\'école')
        return email_school


class RegistrationPackForm(RegistrationForm):
    rgpd_sharing_alumni = forms.BooleanField(
        label=RGPD_AGREEMENT_ALUMNI,
        required=True
    )


class RegistrationAdminForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = [
            'first_name',
            'last_name',
            'email',
            'email_school',
            'phone',
            'birthdate',
            'cursus',
            'promo',
            'amount',
            'paid_on',
            'paid_by'
        ]

    def __init__(self, *args, **kwargs):
        self.is_from_another_school = kwargs.pop("is_from_another_school", False)
        super().__init__(*args, **kwargs)
        if self.is_from_another_school:
            self.fields['original_school'] = forms.CharField(
                max_length=255,
                label="École ou université d'origine"
            )

    cursus = forms.ChoiceField(choices=UserInfos.CursusChoices.choices, label="Cursus")
    promo = forms.IntegerField(label="Promotion")
    amount = forms.IntegerField(label="Montant de la cotisation")
    paid_on = forms.DateField(label="Date du paiement")
    paid_by = forms.ChoiceField(choices=UserMembership.MeanOfPayment.choices)
