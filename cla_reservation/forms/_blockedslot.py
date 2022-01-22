from django import forms


class BlockedSlotForm(forms.ModelForm):
    class Meta:
        model = None
        fields = [
            'name',
            'start_date',
            'start_time',
            'end_time',
            'recurring',
            'recurring_days',
            'end_recurring',
            'admin_display',
            'member_display'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        self.fields['end_recurring'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['end_recurring'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"
