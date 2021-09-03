
from django import forms
from django.core.exceptions import ValidationError


class UploadUserPicture(forms.Form):
    picture = forms.ImageField()

    def clean_picture(self):
        picture = self.cleaned_data.get('picture', False)
        if picture:
            if picture.size > 2621440:
                raise ValidationError("L'image est trop grande ( > 2.5Mo )")
            return picture
        else:
            raise ValidationError("Impossible de lire l'image reçu")
