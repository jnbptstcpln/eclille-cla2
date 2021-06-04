from django import forms

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
        self.fields['type'].queryset = EventRegistrationType.objects.filter(event=self.event, open_to__in=open_to)
