from django import forms
from django.contrib import admin
from django.core.validators import FileExtensionValidator

from cla_member.models import Website, OfficialDocument


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    pass


class OfficialDocumentForm(forms.ModelForm):
    class Meta:
        model = OfficialDocument
        fields = ["type", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].validators.append(FileExtensionValidator(["pdf"]))
        self.fields["file"].widget.attrs["accept"] = "application/pdf"
        self.fields["file"].help_text = "PDF uniquement. Déposer un nouveau fichier remplace l'ancien."


@admin.register(OfficialDocument)
class OfficialDocumentAdmin(admin.ModelAdmin):
    form = OfficialDocumentForm
    list_display = ["type", "file", "updated_at"]

    def has_add_permission(self, request):
        # Un seul document par type : plus d'ajout possible une fois tous les types déposés
        if OfficialDocument.objects.count() >= len(OfficialDocument.Type.choices):
            return False
        return super().has_add_permission(request)
