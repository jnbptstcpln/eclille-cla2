from django import forms
from django.contrib.auth.models import User


class ResetPasswordForm(forms.Form):

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
        label="Identifiant de connexion",
        help_text="Retenez le bien, c'est cet identifiant qui vous permettra de vous connecter",
        required=True,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'prenom.nom'})
    )
    password1 = forms.CharField(
        label="Votre mot de passe",
        help_text="Entre 8 et 35 caractères",
        required=True,
        min_length=8,
        max_length=35,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
    )
    password2 = forms.CharField(
        label="Confirmer votre mot de passe",
        required=True,
        min_length=8,
        max_length=35,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer votre mot de passe'}),
    )

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError('Les mots de passes ne correspondent pas')
        return password2
