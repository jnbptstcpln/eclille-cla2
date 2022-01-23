import bleach
from django import forms
from django.conf import settings
from django.utils import timezone

from cla_reservation.forms._blockedslot import BlockedSlotForm
from cla_reservation.models.synthe import ReservationSynthe, BlockedSlotSynthe


class ReservationSyntheAssociationForm(forms.ModelForm):
    class Meta:
        model = ReservationSynthe
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
        self.fields['description_event'].required = True

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def clean_description_event(self):
        return bleach.clean(
            self.cleaned_data['description_event'],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
        )

class ReservationSyntheMemberForm(forms.ModelForm):
    class Meta:
        model = ReservationSynthe
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'sport_activity',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'input_type') and field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class ReservationSyntheAssociationAdminForm(forms.ModelForm):
    class Meta:
        model = ReservationSynthe
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            'manually_set_datetime',
            'starts_on',
            'ends_on',
            'description_event',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'input_type') or field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def clean_description_event(self):
        return bleach.clean(
            self.cleaned_data['description_event'],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
        )

class ReservationSyntheMemberAdminForm(forms.ModelForm):
    class Meta:
        model = ReservationSynthe
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            'manually_set_datetime',
            'starts_on',
            'ends_on',
            'sport_activity',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'input_type') or field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class ReservationSyntheValidateForm(forms.ModelForm):
    class Meta:
        model = ReservationSynthe
        fields = [
            'starts_on',
            'ends_on',
            'admin_display',
            'member_display'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['starts_on'].help_text = ""
        self.fields['ends_on'].help_text = ""
        # Customising all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'input_type') or field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def save(self, commit=True):
        self.instance.manually_set_datetime = True
        self.instance.validated = True
        self.instance.validated_on = timezone.now()
        return super().save(commit)


class ReservationSyntheRejectForm(forms.ModelForm):
    class Meta:
        model = ReservationSynthe
        fields = [
            'rejected_for'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['rejected_for'].required = True

        # Customising all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'input_type') or field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def save(self, commit=True):
        self.instance.sent = False
        return super().save(commit)


class BlockedSlotSyntheForm(BlockedSlotForm):
    class Meta(BlockedSlotForm.Meta):
        model = BlockedSlotSynthe