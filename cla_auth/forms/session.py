from django import forms


class LoginForm(forms.Form):

    username = forms.CharField(
        label="Identifiant",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'prenom.nom'})
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
