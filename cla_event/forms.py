from django import forms
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.safestring import mark_safe

from cla_event.models import Event


class EventAssociationDefaultForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            'public',
            'name',
            'name_school',
            'type',
            'place',
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            #'presentation_html',
            'poster'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"
        self.fields['start_date'].help_text = mark_safe(f"Pensez à consulter <a target='_blank' href='{resolve_url('cla_event:public:index')}'>le calendrier des évéments</a>")

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class EventAssociationSentForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            #'presentation_html',
            'poster'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class EventCancelForm(forms.ModelForm):

    CANCEL_TYPES = [
        ('show', "Conserver l'événement dans le calendrier avec la mention [ANNULÉ]"),
        ('hide', "Retirer l'événement du calendrier"),
    ]

    class Meta:
        model = Event
        fields = [
            'cancel_type'
        ]

    cancel_type = forms.ChoiceField(choices=CANCEL_TYPES, label="Que souhaitez-vous faire ?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class EventAdminForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            'public',
            'name',
            'name_school',
            'type',
            'place',
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            'manually_set_datetime',
            'starts_on',
            'ends_on',
            #'presentation_html',
            'poster'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class EventValidateForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            'starts_on',
            'ends_on',
            'admin_display',
            'member_display'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def save(self, commit=True):
        self.instance.manually_set_datetime = True
        self.instance.validated = True
        self.instance.validated_on = timezone.now()
        return super().save(commit)


class EventRejectForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'rejected_for'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def save(self, commit=True):
        self.instance.sent = False
        return super().save(commit)
