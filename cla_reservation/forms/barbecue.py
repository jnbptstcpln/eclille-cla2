import bleach
from django import forms
from django.conf import settings
from django.utils import timezone

from cla_reservation.forms._blockedslot import BlockedSlotForm
from cla_reservation.models.barbecue import ReservationBarbecue, BlockedSlotBarbecue


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

    def clean_description_event(self):
        return bleach.clean(
            self.cleaned_data['description_event'],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
        )

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

    def clean_description_user(self):
        return bleach.clean(
            self.cleaned_data['description_user'],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
        )

class ReservationBarbecueAssociationAdminForm(forms.ModelForm):
    class Meta:
        model = ReservationBarbecue
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


class ReservationBarbecueMemberAdminForm(forms.ModelForm):
    class Meta:
        model = ReservationBarbecue
        fields = [
            'start_date',
            'start_time',
            'end_time',
            'multiple_days',
            'manually_set_datetime',
            'starts_on',
            'ends_on',
            'description_user',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs['data-plugin'] = "datepicker"
        self.fields['start_date'].widget.attrs['autocomplete'] = "off"

        # Customising all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'input_type') or field.widget.input_type not in {'checkbox'}:
                field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def clean_description_user(self):
        return bleach.clean(
            self.cleaned_data['description_user'],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
        )

class ReservationBarbecueValidateForm(forms.ModelForm):
    class Meta:
        model = ReservationBarbecue
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


class ReservationBarbecueRejectForm(forms.ModelForm):
    class Meta:
        model = ReservationBarbecue
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


class BlockedSlotBarbecueForm(BlockedSlotForm):
    class Meta(BlockedSlotForm.Meta):
        model = BlockedSlotBarbecue
