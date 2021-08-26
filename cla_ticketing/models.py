import os
import uuid

from django.db import models
from django import forms
from django.utils.text import slugify
from multiselectfield import MultiSelectField
from cla_auth.models import UserInfos
from django_summernote.fields import SummernoteTextField
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def custom_field_file(cls, instance, filename):
        return cls._path(instance, ["cla_ticketing", "custom_field_file"], filename)


class AbstractEvent(models.Model):

    class Meta:
        abstract = True
        ordering = "event_starts_on",

    name = models.CharField(max_length=75, verbose_name="Nom de l'événement")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Identifiant unique de l'événement")
    description = SummernoteTextField(blank=True, verbose_name="Présentation de l'événement")
    organizer = models.CharField(max_length=100, verbose_name="Organisateur de l'événement")
    event_starts_on = models.DateTimeField(verbose_name="Début de l'événement")
    event_ends_on = models.DateTimeField(verbose_name="Fin de l'événement")
    registration_starts_on = models.DateTimeField(verbose_name="Ouverture des inscriptions")
    registration_ends_on = models.DateTimeField(verbose_name="Fermeture des inscriptions")
    colleges = MultiSelectField(choices=UserInfos.Colleges.choices, verbose_name="Collèges autorisés à prendre une place", blank=True)
    places = models.PositiveIntegerField(default=400, verbose_name="Nombre de places")
    contributor_ticketing_href = models.URLField(blank=True, null=True, verbose_name="Lien vers la billeterie d'encaissement pour les cotisants", help_text="Laisser vide si aucune")
    non_contributor_ticketing_href = models.URLField(blank=True, null=True, verbose_name="Lien vers la billeterie d'encaissement pour les non cotisants", help_text="Laisser vide si aucune")
    managers = models.ManyToManyField(User, related_name="+", verbose_name="Administrateurs", help_text="Les administrateurs ont la possiblité de modifier les informations de l'événement ainsi que de gérer la liste des inscrits", blank=True)

    @property
    def are_registrations_opened(self):
        return self.registration_starts_on < timezone.now() <= self.registration_ends_on and self.places_remaining > 0

    @property
    def places_remaining(self):
        return max(self.places-self.registrations.count(), 0)

    def __str__(self):
        return self.name


class AbstractRegistration(models.Model):

    class Meta:
        abstract = True
        ordering = "last_name", "first_name"

    class StudentStatus(models.TextChoices):
        CONTRIBUTOR = 'contributor', 'Cotisant'
        NON_CONTRIBUTOR = 'non_contributor', 'Non cotisant'

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="+", verbose_name="Utilisateur", help_text="Laisser vide si l'inscrit n'est pas un cotisant", null=True, blank=True)
    student_status = models.CharField(max_length=20, choices=StudentStatus.choices, verbose_name="Statut de l'étudiant", editable=False)
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    email = models.EmailField(verbose_name="Adresse mail personnelle")
    phone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="+", verbose_name="Créateur de cette inscription", editable=False, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Inscrit le")
    paid = models.BooleanField(default=False, verbose_name="A payé")

    def __str__(self):
        return f"{self.last_name.upper()} {self.first_name}"

    @property
    def is_contributor(self):
        return self.student_status == self.StudentStatus.CONTRIBUTOR


class AbstractRegistrationCustomField(models.Model):

    class Meta:
        verbose_name = "Champ additionnel"
        verbose_name_plural = "Champs additionnels"
        abstract = True

    class Type(models.TextChoices):
        TEXT = "text", "Texte"
        SELECT = "select", "Choix"
        CHECKBOX = "checkbox", "Case à cocher"
        FILE = "file", "Fichier"

    type = models.CharField(max_length=255, choices=Type.choices, default=Type.TEXT, verbose_name="Type")
    admin_only = models.BooleanField(default=False, verbose_name="Disponible seulement du côté administrateur", blank=True)
    required = models.BooleanField(default=False, verbose_name="Requis", blank=True)
    label = models.CharField(max_length=255, verbose_name="Nom")
    help_text = models.CharField(max_length=255, verbose_name="Description", blank=True)
    options = models.TextField(verbose_name="Options pour le select", help_text="Une valeur par ligne", blank=True, null=True)

    @property
    def field_id(self):
        return slugify(self.label).replace('-', '_')

    def get_field_instance(self, **kwargs):
        return {
            self.Type.TEXT.value: lambda: forms.CharField(
                max_length=255,
                label=self.label,
                help_text=self.help_text,
                required=kwargs.pop('required', self.required),
                **kwargs
            ),
            self.Type.SELECT.value: lambda: forms.ChoiceField(
                choices=[(c.strip(), c.strip()) for c in self.options.split("\n")],
                label=self.label,
                help_text=self.help_text,
                required=kwargs.pop('required', self.required),
                **kwargs
            ),
            self.Type.CHECKBOX.value: lambda: forms.BooleanField(
                label=self.label,
                help_text=self.help_text,
                required=kwargs.pop('required', self.required),
                **kwargs
            ),
            self.Type.FILE.value: lambda: forms.FileField(
                label=self.label,
                help_text=self.help_text,
                required=kwargs.pop('required', self.required),
                **kwargs
            ),
        }.get(self.type)()

    def __str__(self):
        return f"{self.label} ({self.get_type_display()})"


class AbstractRegistrationCustomFieldValueManager(models.Manager):

    def get_or_create_text(self, registration, field, value):
        fv, created = self.get_or_create(
            registration=registration,
            field=field
        )
        fv.text_value = value
        fv.save()
        return fv

    def get_or_create_boolean(self, registration, field, value):
        fv, created = self.get_or_create(
            registration=registration,
            field=field
        )
        fv.boolean_value = value
        fv.save()
        return fv

    def get_or_create_file(self, registration, field, value):
        fv, created = self.get_or_create(
            registration=registration,
            field=field
        )
        fv.file_value = value
        fv.save()
        return fv


class AbstractRegistrationCustomFieldValue(models.Model):

    objects = AbstractRegistrationCustomFieldValueManager()

    class Meta:
        verbose_name = "Champ additionnel"
        verbose_name_plural = "Champs additionnels"
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    registration: AbstractRegistration = None
    field: AbstractRegistrationCustomField = None
    text_value = models.CharField(max_length=255, null=True)
    boolean_value = models.BooleanField(null=True)
    file_value = models.FileField(upload_to=FilePath.custom_field_file)

    @property
    def value(self):
        return {
            AbstractRegistrationCustomField.Type.TEXT.value: lambda: self.text_value,
            AbstractRegistrationCustomField.Type.SELECT.value: lambda: self.text_value,
            AbstractRegistrationCustomField.Type.CHECKBOX.value: lambda: self.boolean_value,
            AbstractRegistrationCustomField.Type.FILE.value: lambda: self.file_value
        }.get(self.field.type)()


class Event(AbstractEvent):

    class Meta:
        abstract = False
        verbose_name = "Billeterie d'événement"
        verbose_name_plural = "Billeteries d'événement"
        permissions = (
            ('event_manager', "Accès à l'interface de gestion des événements pour lesquels l'utilisateur est administrateur"),
        )

    @staticmethod
    def get_or_create_event_organizer_group():
        group, created = Group.objects.get_or_create(name="Organisateur d'événements")
        if created and group.permissions.filter(codename="event_manager").count() == 0:
            group.permissions.add(Permission.objects.get(codename='event_manager'))
        return group

    allow_non_contributor_registration = models.BooleanField(default=False, verbose_name="Autoriser l'inscription des non cotisants")


class EventRegistrationCustomField(AbstractRegistrationCustomField):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="custom_fields", verbose_name="Champs additionnels")


class EventRegistrationType(models.Model):

    class Meta:
        verbose_name = "Type de place"
        verbose_name_plural = "Types de place"

    class OpenTo(models.TextChoices):
        CONTRIBUTOR = 'contributors', 'Cotisants'
        NON_CONTRIBUTOR = 'non_contributors', 'Non cotisants'
        BOTH = 'both', 'Cotisants et non cotisants'

    name = models.CharField(max_length=75, verbose_name="Nom")
    open_to = models.CharField(max_length=75, choices=OpenTo.choices, verbose_name="Ouvert aux", default=OpenTo.BOTH)
    description = models.CharField(max_length=250, verbose_name="Description", blank=True)
    price = models.FloatField(blank=True, verbose_name="Prix")
    visible = models.BooleanField(default=True, blank=True, verbose_name="Accessible")
    event = models.ForeignKey(Event, related_name="registration_types", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.price}€"


class EventRegistration(AbstractRegistration):

    class Meta:
        abstract = False
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"

    type = models.ForeignKey(EventRegistrationType, related_name="registrations", null=True, on_delete=models.SET_NULL)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations", verbose_name="Evénement", editable=False)


class EventRegistrationCustomFieldValue(AbstractRegistrationCustomFieldValue):
    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE, related_name="custom_fields", editable=False)
    field = models.ForeignKey(EventRegistrationCustomField, on_delete=models.CASCADE, related_name="+", editable=False)


class DancingParty(AbstractEvent):

    class Meta:
        abstract = False
        verbose_name = "Billeterie de soirée dansante"
        verbose_name_plural = "Billeteries de soirée dansante"

    scanners = models.ManyToManyField(User, related_name="+", verbose_name="Scanneurs", help_text="Les scanneurs peuvent effectuer les entrées au sein de l'événement", blank=True)

    @property
    def places_remaining(self):
        return max(self.places-self.registrations.filter(is_staff=False).count(), 0)


class DancingPartyRegistrationCustomField(AbstractRegistrationCustomField):
    dancing_party = models.ForeignKey(DancingParty, on_delete=models.CASCADE, related_name="custom_fields", verbose_name="Champs additionnels")


class DancingPartyRegistration(AbstractRegistration):

    class Meta:
        abstract = False
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        permissions = (
            ('dancingparty_manager', "Accès à l'interface de gestion des soirées dansantes pour lesquelles l'utilisateur est administrateur"),
        )
        unique_together = [
            ['user', 'dancing_party', ],  # User can only be registered one time for an event
        ]

    class Types(models.TextChoices):
        HARD = "hard", "Avec alcool"
        SOFT = "soft", "Sans alcool"

        @classmethod
        def get_price(cls, student_status, type):
            return {
                (AbstractRegistration.StudentStatus.CONTRIBUTOR, cls.SOFT): 4,
                (AbstractRegistration.StudentStatus.CONTRIBUTOR, cls.HARD): 6,
                (AbstractRegistration.StudentStatus.NON_CONTRIBUTOR, cls.SOFT): 8,
                (AbstractRegistration.StudentStatus.NON_CONTRIBUTOR, cls.HARD): 10
            }.get((student_status, type))

    dancing_party = models.ForeignKey(DancingParty, on_delete=models.CASCADE, related_name="registrations", verbose_name="Soirée dansante", editable=False)
    validated = models.BooleanField(default=False, verbose_name="Validée")
    is_staff = models.BooleanField(default=False)
    type = models.CharField(max_length=255, choices=Types.choices, default=None, verbose_name="Place", null=True)
    staff_description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Staff")
    home = models.CharField(max_length=100, verbose_name="Logement après la soirée")
    birthdate = models.DateField(verbose_name="Date de naissance")
    guarantor = models.ForeignKey(User, on_delete=models.DO_NOTHING, to_field="username", related_name="+", verbose_name="Garant", null=True)

    @property
    def price(self):
        return self.Types.get_price(self.student_status, self.type)


class DancingPartyRegistrationCustomFieldValue(AbstractRegistrationCustomFieldValue):
    registration = models.ForeignKey(DancingPartyRegistration, on_delete=models.CASCADE, related_name="custom_fields", editable=False)
    field = models.ForeignKey(DancingPartyRegistrationCustomField, on_delete=models.CASCADE, related_name="+", editable=False)