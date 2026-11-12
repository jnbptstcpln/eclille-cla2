from django.db import models
from django.forms import fields
from django_summernote.widgets import SummernoteWidget


# Copie des champs de django-summernote 0.8.11.6. Depuis la 0.8.20, ses champs passent le contenu dans
# bleach.clean(styles=...) : plantage sur None (migrations) et argument supprimé de bleach 5+.
# Le contenu est nettoyé (ou non) par chaque formulaire, comme avant.
class SummernoteTextFormField(fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'widget': SummernoteWidget()})
        super().__init__(*args, **kwargs)


class SummernoteTextField(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': SummernoteTextFormField})
        return super().formfield(**kwargs)
