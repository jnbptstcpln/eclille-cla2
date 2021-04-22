from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):

    class Validators:

        @classmethod
        def validate_username(cls, value):
            try:
                user = User.objects.get(username=value)
                if hasattr(user, 'infos'):
                    if user.infos.activated_on is None:
                        raise forms.ValidationError("Ce compte n'a pas encore été activé, veuillez consulter votre adresse mail en @xxxx.centralelille.fr")
            except User.DoesNotExist:
                pass

    username = forms.CharField(
        label="Identifiant",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'prenom.nom'}),
        validators=[Validators.validate_username]
    )
    password = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )
    stay_logged_in = forms.BooleanField(
        label="Rester connecté",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
