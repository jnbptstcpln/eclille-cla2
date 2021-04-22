from django import forms
from django.contrib.auth.models import User


class ValidationForm(forms.Form):

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

    validation_code = forms.CharField(
        label="Code à 6 chiffres reçu par mail",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456'})
    )
    cursus = forms.ChoiceField(
        label="Vous êtes actuellement...",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def validate_code(self, value):
        validation_request = self.user.infos.validation_request
        if validation_request.attempt > 10:
            raise forms.ValidationError("Vous avez dépassé le nombre maximal d'essais, veuillez contacter cla@centralelille.fr")

        validation_request.attempt += 1

        if validation_request.code != int(value):
            raise forms.ValidationError("Le code que vous avez indiqué est incorrect...")
        else:
            validation_request.used = True

        validation_request.save()

    def __init__(self, *args, user: User = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['validation_code'].validators.append(self.validate_code)
        self.fields['cursus'] = self.user.infos.next_cursus_choices.choices
