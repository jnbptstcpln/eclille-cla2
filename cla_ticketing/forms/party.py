from django import forms

from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.auth.models import User
from django.utils import timezone
from cla_ticketing.models import DancingPartyRegistration


class ContributorDancingPartyRegistrationAdminForm(forms.ModelForm):

    class Meta:
        model = DancingPartyRegistration

        fields = [
            "user",
            "type",
            "staff_description",
            "home"
        ]

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(infos__valid_until__gt=timezone.now()),
        label="Étudiant",
        help_text="Si l'étudiant n'apparait pas dans les résultats c'est que son compte n'est pas activé.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = ForeignKeyRawIdWidget(self.instance._meta.fields.get('user'), admin.site)


class NonContributorDancingPartyRegistrationAdminForm(forms.ModelForm):

    class Meta:
        model = DancingPartyRegistration
        fields = [

        ]