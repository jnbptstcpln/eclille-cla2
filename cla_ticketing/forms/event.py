from django import forms
from django.core.exceptions import ValidationError

from cla_ticketing.models import EventRegistration, EventRegistrationType


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'type'
        ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.student_status = kwargs.pop('student_status')
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        open_to = {
            EventRegistrationType.OpenTo.BOTH,
            (EventRegistrationType.OpenTo.CONTRIBUTOR if self.student_status == EventRegistration.StudentStatus.CONTRIBUTOR else EventRegistrationType.OpenTo.NON_CONTRIBUTOR)
        }
        self.fields['type'].queryset = EventRegistrationType.objects.filter(event=self.event, open_to__in=open_to, visible=True)


class AdminEventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = [
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'type',
            'paid'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        non_required = 'first_name', 'last_name', 'email', 'phone'
        for field_name in non_required:
            self.fields[field_name].required = False
            self.fields[field_name].help_text = "Sera automatiquement rempli si un utilisateur est sélectionné"

    def clean_first_name(self):
        user = self.cleaned_data.get('user')
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) == 0:
            if user:
                return user.first_name
            raise ValidationError("Ce champ doit être renseigné")
        return first_name

    def clean_last_name(self):
        user = self.cleaned_data.get('user')
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) == 0:
            if user:
                return user.last_name
            raise ValidationError("Ce champ doit être renseigné")
        return last_name

    def clean_email(self):
        user = self.cleaned_data.get('user')
        email = self.cleaned_data.get('email')
        if len(email) == 0:
            if user:
                return user.email
            raise ValidationError("Ce champ doit être renseigné")
        return email

    def clean_phone(self):
        user = self.cleaned_data.get('user')
        phone = self.cleaned_data.get('phone')
        if len(phone) == 0:
            if user:
                if hasattr(user, 'infos'):
                    return user.infos.phone
                return "Non renseigné"
            raise ValidationError("Ce champ doit être renseigné")
        return phone
