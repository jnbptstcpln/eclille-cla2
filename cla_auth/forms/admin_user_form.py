from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify


class UserCreationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].label = "Adresse mail personnelle"

    def save(self, commit=True):
        user = super().save(commit=False)
        _first_name = self.cleaned_data['first_name'].replace(' ', '').replace('-', '')
        _last_name = self.cleaned_data['last_name'].replace(' ', '').replace('-', '')
        user.username = f"{slugify(_first_name)}.{slugify(_last_name)}"
        if commit:
            user.save()
        return user
