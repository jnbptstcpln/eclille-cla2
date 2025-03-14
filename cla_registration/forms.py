from django import forms
from django.utils import timezone

from .models import Registration, ImageRightAgreement

from cla_auth.forms.admin_user_form import UserCreationForm
from cla_auth.models import UserInfos, UserMembership
from cla_registration.strings import RGPD_AGREEMENT_CLA, RGPD_AGREEMENT_ALUMNI
from cla_registration.utils import capitalize_name


class AbstractRegistrationForm(forms.ModelForm):

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
        ]

    rgpd_agreement = forms.BooleanField(
        label=RGPD_AGREEMENT_CLA,
        required=True
    )

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

    def clean_email_school(self):
        email = self.cleaned_data['email']
        email_school = self.cleaned_data['email_school']
        if not email_school.endswith(self.school_domain):
            raise forms.ValidationError(f"Veuillez vérifier que votre adresse mail scolaire finit bien en @{self.school_domain}")
        if email == email_school:
            raise forms.ValidationError('Veuillez indiquer une adresse mail personnelle différente de votre adresse mail fournie par l\'école')
        return email_school

    def clean_first_name(self):
        return capitalize_name(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return capitalize_name(self.cleaned_data['last_name'])


class RegistrationForm(AbstractRegistrationForm):

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

    rgpd_sharing_alumni = forms.BooleanField(
        label=RGPD_AGREEMENT_ALUMNI,
        required=False
    )


class RegistrationPackForm(RegistrationForm):
    rgpd_sharing_alumni = forms.BooleanField(
        label=RGPD_AGREEMENT_ALUMNI,
        required=True
    )


class EnsclRegistrationForm(AbstractRegistrationForm):

    def save(self, commit=True):
        self.instance.rgpd_sharing_alumni = False
        return super().save(commit)


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
            'paid_by',
            'paiement_method',
            'paid_validated'
        ]

    def __init__(self, *args, **kwargs):
        self.is_from_another_school = kwargs.pop("is_from_another_school", False)
        self.is_pack_available = kwargs.pop("is_pack_available", False)
        
        super().__init__(*args, **kwargs)
        
        if self.is_from_another_school:
            self.fields['original_school'] = forms.CharField(
                max_length=255,
                label="École ou université d'origine"
            )
        
        
        if self.is_pack_available:
            self.fields['pack'] = forms.ChoiceField(
                choices=[(1, "L'étudiant veut cotiser au pack"), (0, "L'étudiant ne veut pas cotiser au pack"),],
                label="Pack Alumni",
                help_text="Pensez à mettre à jour ce champ et le montant de la cotisation si l'étudiant a changé d'avis"
            )

    cursus = forms.ChoiceField(choices=UserInfos.CursusChoices.choices, label="Cursus")
    promo = forms.IntegerField(label="Promotion")
    amount = forms.IntegerField(label="Montant de la cotisation")
    paid_on = forms.DateField(label="Date du paiement")
    paid_by = forms.ChoiceField(label="Moyen de paiement", choices=UserMembership.MeanOfPayment.choices)
    paiement_method = forms.ChoiceField(label="Méthode de paiement", choices=UserMembership.PaymentMethod.choices)
    paid_validated = forms.BooleanField(label="Paiement effectué", required=False, help_text="Ne pas cocher si le paiement sera effectué plus tard, pour les virements par exemple")


class ImageRightForm(forms.ModelForm):

    school_domain = None

    class Meta:
        model = ImageRightAgreement
        fields = 'first_name', 'last_name', 'birthdate', 'email_school'

    def __init__(self, *args, **kwargs):
        self.school_domain = kwargs.pop("school_domain")
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['placeholder'] = f"Prénom"
        self.fields['first_name'].widget.attrs['autocomplete'] = f"off"

        self.fields['last_name'].widget.attrs['placeholder'] = f"Nom"
        self.fields['last_name'].widget.attrs['autocomplete'] = f"off"

        self.fields['birthdate'].widget.attrs['placeholder'] = f"DD/MM/YYYY"
        self.fields['birthdate'].widget.attrs['autocomplete'] = f"off"

        self.fields['email_school'].widget.attrs['placeholder'] = f"prenom.nom@{self.school_domain}"
        self.fields['email_school'].widget.attrs['autocomplete'] = f"off"
        self.fields['email_school'].help_text = "Vous trouverez cette adresse dans les documents que vient de vous remettre l'administration de Centrale."

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control form-control-sm"

    def clean_email_school(self):
        email_school = self.cleaned_data['email_school']
        if not email_school.endswith(self.school_domain):
            raise forms.ValidationError(f"Veuillez vérifier que votre adresse mail scolaire finit bien en @{self.school_domain}")

        if ImageRightAgreement.objects.filter(email_school=email_school, created_on__year=timezone.now().year).count() > 0:
            raise forms.ValidationError(f"Cette adresse mail a déjà remplie ce formulaire")
        return email_school

    def clean_first_name(self):
        return capitalize_name(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return capitalize_name(self.cleaned_data['last_name'])


class ImageRightSignForm(forms.Form):
    signature = forms.CharField(widget=forms.HiddenInput())
