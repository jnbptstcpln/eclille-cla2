from django.db import models
from multiselectfield import MultiSelectField
from cla_auth.models import UserInfos
from django_summernote.fields import SummernoteTextField
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone


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
        return self.registration_starts_on < timezone.now() <= self.registration_ends_on

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
    phone = models.CharField(max_length=15, verbose_name="Numéro de téléphone")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="+", verbose_name="Créateur de cette inscription", editable=False, null=True)
    created_on = models.DateTimeField(auto_now=True, editable=False)
    paid = models.BooleanField(default=False, verbose_name="A payer")

    def __str__(self):
        return f"{self.last_name.upper()} {self.first_name}"

    @property
    def is_contributor(self):
        return self.student_status == self.StudentStatus.CONTRIBUTOR


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


class DancingParty(AbstractEvent):

    class Meta:
        abstract = False
        verbose_name = "Billeterie de soirée dansante"
        verbose_name_plural = "Billeteries de soirée dansante"


class DancingPartyRegistration(AbstractRegistration):

    class Meta:
        abstract = False
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"

    dancing_party = models.ForeignKey(DancingParty, on_delete=models.CASCADE, related_name="registrations", verbose_name="Soirée dansante", editable=False)
    home = models.CharField(max_length=100, verbose_name="Logement après la soirée")
    birthdate = models.DateField(verbose_name="Date de naissance")
