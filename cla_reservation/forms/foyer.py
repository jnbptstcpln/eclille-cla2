from django import forms

from cla_reservation.models.foyer import ReservationFoyer, FoyerItem


class ReservationFoyerAssociationForm(forms.ModelForm):
    class Meta:
        model = ReservationFoyer
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            'description',
            'items',
            'beer_selection',
        ]

    items = forms.ModelMultipleChoiceField(
        label="Équipements supplémentaires",
        queryset=FoyerItem.objects.filter(available=True),
        widget=forms.CheckboxSelectMultiple(attrs={'display': 'normal'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'input_type') or field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"
