from django import forms

from cla_association.models import Association
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
            'presentation_html',
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


class EventAssociationSentForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            'presentation_html',
            'poster'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"
