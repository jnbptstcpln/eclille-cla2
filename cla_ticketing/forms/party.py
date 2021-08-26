from django import forms

from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.auth.models import User
from django.utils import timezone
from cla_ticketing.models import DancingPartyRegistration


class DancingPartyRegistrationAdminForm(forms.Form):

    class Meta:
        model = DancingPartyRegistration
        fields = 'pass_sanitaire',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
