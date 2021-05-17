from django import forms
from django.contrib.auth.models import User

from cla_auth.models import Service


class ValidationForm(forms.Form):

    rgpd_agreement = forms.BooleanField(
        label="J\'accepte que mes informations soient utilisées par Centrale Lille Associations tel que décrit et détaillé dans la charte de confidentialité.",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, service: Service, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rgpd_agreement'].label.format(service.domain)
