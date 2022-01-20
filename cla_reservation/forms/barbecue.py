from django import forms

from cla_reservation.models.barbecue import ReservationBarbecue


class ReservationBarbecueAssociationForm(forms.ModelForm):
    class Meta:
        model = ReservationBarbecue
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            'description_event',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class ReservationBarbecueMemberForm(forms.ModelForm):
    class Meta:
        model = ReservationBarbecue
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'description_user',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"
