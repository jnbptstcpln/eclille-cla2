import bleach as bleach
from django import forms

from cla_association.models import Association, HandoverFolder
from django.conf import settings


class AssociationForm(forms.ModelForm):

    class Meta:
        model = Association
        fields = ['description', 'presentation_html']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['description'].help_text = "La description rapide est affichée dans la liste des associations"
        self.fields['presentation_html'].help_text = "La présentation est affichée sur la page dédiée à votre association"

        # Customising all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"

    def clean_presentation_html(self):
        return bleach.clean(
            self.cleaned_data['presentation_html'],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
        )


class AssociationLogoForm(forms.ModelForm):
    class Meta:
        model = Association
        fields = ['logo']
        widgets = {
            'logo': forms.FileInput(attrs={
                'class': 'form-control d-block'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"


class HandoverFolderForm(forms.ModelForm):

    class Meta:
        model = HandoverFolder
        fields = [
            'quitus',
            'archive'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customising all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', "") + "form-control"
            field.required = True
