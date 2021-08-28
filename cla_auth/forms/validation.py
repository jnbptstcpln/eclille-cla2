from django import forms
from django.contrib.auth.models import User

from cla_auth.models import Service


class ValidationForm(forms.Form):
    validation_code = forms.BooleanField(
        label="Code à six chiffres",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user: User = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['cursus'] = forms.ChoiceField(
            label="Votre cursus actuel",
            choices=self.user.infos.next_cursus_choices.choices,
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'})
        )
