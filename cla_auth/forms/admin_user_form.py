from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.forms import UserChangeForm as Auth_UserChangeForm


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


class UserChangeForm(Auth_UserChangeForm):
    def __init__(self, *args, reset_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # Password field customization
        password = self.fields.get('password')
        if password:
            if hasattr(self.instance, "infos"):
                if self.instance.infos.activated_on is not None:
                    if reset_request:  # User did request password reset
                        password.help_text = (
                            "L'utilisateur a demandé à réinitialiser son mot de passe "
                            "transmettez lui le lien suivant : <a href={href}>{href}</a>"
                        ).format(href="https://google.com")
                    else:
                        password.help_text = (
                            "Vous avez la possiblité de lancer la procédure de réinitialisation "
                            "de mot de passe à l'aide de <a href='{}'>ce formulaire</a>"
                        ).format('../password-reset')
                else:
                    password.help_text = (
                        "L'utilisateur n'a pas encore activé son compte."
                    )
