import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import resolve_url
from django_resized import ResizedImageField
from django_summernote.fields import SummernoteTextField

from cla_auth.models import UserInfos, Service


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s-%s.%s" % (uuid.uuid4(), instance.slug, ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def association_logo(cls, instance, filename):
        return cls._path(instance, ["cla_association", "association_logo"], filename)


class AssociationManager(models.Manager):

    def get_cla(self):
        try:
            return self.get(slug="cla")
        except self.model.DoesNotExist:
            return self.create(
                name="CLA",
                subtitle="Centrale Lille Associations",
                slug="cla",
                type=self.model.Types.ASSOC_1901,
                category=self.model.Category.BDX,
                description="Centrale Lille Associations est une association loi 1901 fondée en 2008, continuation de plus d'un siècle et demi de développement perpétuel des structures associatives de Centrale Lille par ses étudiants.",
                display=False
            )

    def get_bde(self):
        try:
            return self.get(slug="bde")
        except self.model.DoesNotExist:
            return self.create(
                name="BDE",
                subtitle="Bureau des élèves",
                slug="bde",
                type=self.model.Types.BDX,
                category=self.model.Category.BDX,
                description="Le BDE est le bureau des élèves de l'école Centrale de Lille",
                display=False
            )


class Association(models.Model):

    objects = AssociationManager()

    class Meta:
        verbose_name = "Association"
        verbose_name_plural = "Associations"
        ordering = "name",

    class Types(models.TextChoices):
        CLUB = "club", "Club de CLA"
        COMMISSION = "commission", "Commission de CLA"
        BDX = "bdx", "BDX"
        ASSOC_1901 = "asso_1901", "Association loi 1901"

    class Category(models.TextChoices):
        AUDIOVISUAL = "audiovisual", "Audiovisuel"
        SPORT = "sport", "Autour du sport"
        BDX = "bdx", "BDX"
        BDX_LIST = "bdx_list", "BDX (Liste)"
        FOREIGN_CULTURE = "foreign_cuture", "Culture étrangère"
        WRITING_DRAWING = "writing_drawing", "Écriture et dessin"
        OPEN_MINDED = "open_minded", "Esprit d'ouverture"
        EVENTS = "events", "Évènements"
        GASTRONOMY = "gastronomy", "Gastronomie"
        ENTERPRISES = "enterprises", "Monde de l'entreprise"
        ENGINEERING = "engineering", "Monde de l'ingénieur"
        MUSIC = "music", "Musique"
        SOLIDARITY = "solidarity", "Solidarité"
        THEATER_CINEMA = "theater_cinema", "Théâtre et cinéma"
        RESIDENCE_LIFE = "residence_life", "Vie sur la résidence"
        OTHER = "other", "Autre"

    name = models.CharField(max_length=100, verbose_name="Nom de l'association")
    subtitle = models.CharField(max_length=100, verbose_name="Sous-titre", null=True, blank=True)
    slug = models.SlugField(verbose_name="Identifiant unique de l'association")
    type = models.CharField(max_length=250, choices=Types.choices, verbose_name="Forme juridique")
    category = models.CharField(max_length=250, choices=Category.choices, verbose_name="Catégorie")
    description = models.TextField(max_length=350, verbose_name="Description rapide")
    presentation_html = SummernoteTextField(verbose_name="Présentation de l'association", blank=True)
    logo = ResizedImageField(size=[500, 500], force_format="PNG", upload_to=FilePath.association_logo, null=True, blank=True, verbose_name="Logo de l'association")

    display = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    active = models.BooleanField(default=True, verbose_name="Active", help_text="Une association active peut effectuer des demandes de réservation du foyer, du synthé, du barbecue...")

    def get_absolute_url(self):
        return resolve_url("cla_association:public:detail", self.slug)

    @property
    def is_club_or_commission(self):
        return self.type in {
            self.Types.CLUB,
            self.Types.COMMISSION
        }

    def __str__(self):
        return self.name


class AssociationMember(models.Model):

    class Meta:
        verbose_name = "Poste"
        verbose_name_plural = "Postes"
        ordering = "_role", "_role_custom"

    class Roles(models.TextChoices):
        PRESIDENT = "010_president", "Président"
        GENERAL_SECRETARY = "020_general_secretary", "Secrétaire général"
        TREASURER = "030_treasurer", "Trésorier"
        SECRETARY = "040_secretary", "Secrétaire"
        VICE_PRESIDENT = "050_vice_president", "Vice président"
        VICE_PRESIDENT_I = "051_vice_president_i", "VPI"
        VICE_PRESIDENT_E = "052_vice_president_e", "VPE"
        RESPO_EVENT = "100_respo_event", "Responsable événement"
        CUSTOM = "999_custom", "Personnalisé"

    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="association_memberships", null=True, blank=True, verbose_name="Étudiant")
    _role = models.CharField(max_length=250, choices=Roles.choices, verbose_name="Poste")
    _role_custom = models.CharField(max_length=250, null=True, blank=True, verbose_name="Poste personnalisé", help_text="A indiquer avec le poste \"Personnalisé\"")

    @property
    def role(self):
        if self._role == self.Roles.CUSTOM:
            return self._role_custom
        return self.get__role_display()

    def __str__(self):
        return self.role


class AssociationLink(models.Model):

    class Meta:
        verbose_name = "Liens"
        verbose_name_plural = "Liens"
        ordering = "_type", "_type_custom"

    class Types(models.TextChoices):
        WEBSITE = "000_website", "Site web"
        FACEBOOK = "010_facebook", "Facebook"
        TWITTER = "020_twitter", "Twitter"
        INSTAGRAM = "030_instagram", "Instagram"
        TIKTOK = "040_tiktok", "Tiktok"
        TWITCH = "050_twitch", "Twitch"
        YOUTUBE = "060_youtube", "YouTube"
        CUSTOM = "999_custom", "Personnalisé"

    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name="links")
    _type = models.CharField(max_length=250, choices=Types.choices, verbose_name="Poste")
    _type_custom = models.CharField(max_length=250, null=True, blank=True, verbose_name="Type personnalisé", help_text="A indiquer avec le type \"Personnalisé\"")
    href = models.URLField(verbose_name="Lien")

    @property
    def type_value(self):
        return self._type

    @property
    def type(self):
        if self._type == self.Types.CUSTOM:
            return self._type_custom
        return self.get__type_display()

    def __str__(self):
        return self.type
