from django import forms
from .models import Registration


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
        super().__init__(*args, **kwargs)
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
        label="J'accepte que mes informations soient utilisées par Centrale Lille Associations tel que décrit et détaillé dans <a href='/privacy/' target='blank'>la charte de confidentialité</a>",
        required=True
    )
    rgpd_sharing_alumni = forms.BooleanField(
        label="J’accepte que mes coordonnées soient transmises à Centrale Lille Alumni dans le cadre du partenariat avec Centrale Lille Associations, pour la création de mon compte sur le site du réseau (www.centraliens-lille.org) et l’accès aux services liés (événements, mentorat, offres de stages, etc.)",
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
        label="J’accepte que mes coordonnées soient transmises à Centrale Lille Alumni dans le cadre du partenariat avec Centrale Lille Associations, pour la création de mon compte sur le site du réseau (www.centraliens-lille.org) et l’accès aux services liés (événements, mentorat, offres de stages, etc.)",
        required=True
    )
