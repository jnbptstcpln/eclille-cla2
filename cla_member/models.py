import os
import uuid

from django.db import models
from multiselectfield import MultiSelectField

from cla_auth.models import UserInfos, Service


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def website_visual(cls, instance, filename):
        return cls._path(instance, ["cla_member", "website_visual"], filename)


class Website(models.Model):

    class Meta:
        verbose_name = "Site partenaire"
        verbose_name_plural = "Sites partenaires"

    name = models.CharField(max_length=100, verbose_name="Nom du site")
    description = models.TextField(max_length=255, verbose_name="Description")
    href = models.CharField(max_length=250, verbose_name="Lien vers le site")
    colleges = MultiSelectField(choices=UserInfos.Colleges.choices, verbose_name="Collèges concernés", blank=True)
    contributor_only = models.BooleanField(default=False, verbose_name="Afficher seulement aux comptes validés")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name="Service associé")
    display = models.BooleanField(default=True, verbose_name="Afficher le site dans l'espace adhérent")
    visual = models.ImageField(upload_to=FilePath.website_visual, null=True, blank=True, verbose_name="Visuel du site")

    def __str__(self):
        return self.name
