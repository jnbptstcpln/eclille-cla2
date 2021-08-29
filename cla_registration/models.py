from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from cla_web.utils import next_back_to_school_year


class RegistrationSessionManager(models.Manager):

    def get_current_registration_session(self):
        return self.filter(date_start__lte=timezone.now(), date_end__gt=timezone.now()).first()


class RegistrationSession(models.Model):

    class Meta:
        verbose_name = "Campagne d'adhésion"
        verbose_name_plural = "Campagnes d'adhésion"
        ordering = "-date_start",

    objects = RegistrationSessionManager()

    class DefaultTicketingHref:

        @staticmethod
        def ticketing_href_centrale_pack():
            return f"https://billetterie.pumpkin-app.com/cla-{next_back_to_school_year()}-centrale-pack"

        @staticmethod
        def ticketing_href_centrale_cla():
            return f"https://billetterie.pumpkin-app.com/cla-{next_back_to_school_year()}-centrale-cla"

        @staticmethod
        def ticketing_href_centrale_dd_pack():
            return f"https://billetterie.pumpkin-app.com/cla-{next_back_to_school_year()}-centrale-dd-pack"

        @staticmethod
        def ticketing_href_centrale_dd_cla():
            return f"https://billetterie.pumpkin-app.com/cla-{next_back_to_school_year()}-centrale-dd-cla"

        @staticmethod
        def ticketing_href_iteem_pack():
            return f"https://billetterie.pumpkin-app.com/cla-{next_back_to_school_year()}-iteem-pack"

        @staticmethod
        def ticketing_href_iteem_cla():
            return f"https://billetterie.pumpkin-app.com/cla-{next_back_to_school_year()}-iteem-cla"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    school_year = models.PositiveIntegerField(verbose_name="Année de la rentrée scolaire", default=next_back_to_school_year)
    date_start = models.DateField(verbose_name="Date d'ouverture des inscriptions")
    date_end = models.DateField(verbose_name="Date de fermeture des inscriptions")

    ticketing_href_centrale_pack = models.URLField(
        null=True,
        blank=True,
        verbose_name="Billetterie \"[Centrale Lille] Pack Alumni+CLA\"",
        default=DefaultTicketingHref.ticketing_href_centrale_pack
    )
    ticketing_href_centrale_cla = models.URLField(
        null=True,
        blank=True,
        verbose_name="Billetterie \"[Centrale Lille] Adhésion CLA\"",
        default=DefaultTicketingHref.ticketing_href_centrale_cla
    )
    ticketing_href_centrale_dd_pack = models.URLField(
        null=True,
        blank=True,
        verbose_name="Billetterie \"[Centrale Lille][Double diplôme] Pack Alumni+CLA\"",
        default=DefaultTicketingHref.ticketing_href_centrale_dd_pack
    )
    ticketing_href_centrale_dd_cla = models.URLField(
        null=True,
        blank=True,
        verbose_name="Billetterie \"[Centrale Lille][Double diplôme] Adhésion CLA\"",
        default=DefaultTicketingHref.ticketing_href_centrale_dd_cla
    )
    ticketing_href_iteem_pack = models.URLField(
        null=True,
        blank=True,
        verbose_name="Billetterie \"[ITEEM] Pack Alumni+CLA\"",
        default=DefaultTicketingHref.ticketing_href_iteem_pack
    )
    ticketing_href_iteem_cla = models.URLField(
        null=True,
        blank=True,
        verbose_name="Billetterie \"[ITEEM] Adhésion CLA\"",
        default=DefaultTicketingHref.ticketing_href_iteem_cla
    )

    sharing_uuid_alumni = models.UUIDField(default=uuid4, verbose_name="Identifiant de partage avec les Alumni", editable=False)

    def stats(self):
        class Stats:
            def __init__(self, session: RegistrationSession):
                self.session = session

                self.total_nb = self.session.registrations.count()

                self.validated_nb = self.session.registrations.filter(account_id__isnull=False).count()
                self.validated_pc = round(self.validated_nb/self.total_nb * 100) if self.total_nb > 0 else 0

                self.pack_nb = self.session.registrations.filter(pack=True).count()
                self.pack_pc = round(self.pack_nb/self.total_nb * 100) if self.total_nb > 0 else 0

                self.pack_validated_nb = self.session.registrations.filter(pack=True, account_id__isnull=False).count()

                self.school_centrale_nb = self.session.registrations.filter(school=Registration.SchoolDomains.CENTRALE).count()
                self.school_iteem_nb = self.session.registrations.filter(school=Registration.SchoolDomains.ITEEM).count()

        return Stats(self)

    @property
    def are_registrations_opened(self):
        return self.date_start <= timezone.now() < self.date_end

    def __str__(self):
        return f"{self.school_year}"


class Registration(models.Model):

    class Meta:
        verbose_name = "Formulaire d'adhésion"
        verbose_name_plural = "Formulaires d'adhésion"

    class SchoolDomains(models.TextChoices):
        CENTRALE = "centrale.centralelille.fr", "École Centrale de Lille"
        ITEEM = "iteem.centralelille.fr", "ITEEM"
        ENSCL = "enscl.centralelille.fr", "ENSCL"

    class Types(models.TextChoices):
        CENTRALE_PACK = "centrale_pack", "[Centrale Lille] Pack Alumni+CLA"
        CENTRALE_CLA = "centrale_cla", "[Centrale Lille] Adhésion CLA"
        CENTRALE_DD_PACK = "centrale_dd_pack", "[Centrale Lille][Double diplôme] Pack Alumni+CLA"
        CENTRALE_DD_CLA = "centrale_dd_cla", "[Centrale Lille][Double diplôme] Adhésion CLA"
        ITEEM_PACK = "iteem_pack", "[ITEEM] Pack Alumni+CLA"
        ITEEM_CLA = "iteem_cla", "[ITEEM] Adhésion CLA"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    datetime_registration = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Date de l'inscription")
    session = models.ForeignKey(RegistrationSession, related_name="registrations", on_delete=models.CASCADE)
    account = models.OneToOneField(User, related_name="registration", on_delete=models.SET_NULL, null=True, default=None, editable=False)
    type = models.CharField(max_length=255, choices=Types.choices, verbose_name="Type d'adhésion", null=True)
    first_name = models.CharField(max_length=255, verbose_name="Prénom")
    last_name = models.CharField(max_length=255, verbose_name="Nom")
    email = models.EmailField(verbose_name="Adresse mail personnelle")
    email_school = models.EmailField(verbose_name="Adresse mail scolaire")
    phone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    birthdate = models.DateField(verbose_name="Date de naissance")
    school = models.TextField(max_length=255, choices=SchoolDomains.choices, verbose_name="Ecole")
    original_school = models.CharField(max_length=255, verbose_name="École/université d'origine", null=True)
    pack = models.BooleanField(verbose_name="L'étudiant a choisi de cotiser avec le pack")
    contribution = models.PositiveIntegerField(verbose_name="Montant de cotisation à régler")
    rgpd_agreement = models.BooleanField(verbose_name="L'étudiant a accepté que ses informations soient stockées et utilisées par Centrale Lille Associations")
    rgpd_sharing_alumni = models.BooleanField(verbose_name="L'étudiant a accepté que ses informations soient partagées avec Centrale Lille Alumni")

    @property
    def ticketing_href(self):
        return {
            self.Types.CENTRALE_PACK: self.session.ticketing_href_centrale_pack,
            self.Types.CENTRALE_DD_PACK: self.session.ticketing_href_centrale_dd_pack,
            self.Types.ITEEM_PACK: self.session.ticketing_href_iteem_pack,
            self.Types.CENTRALE_CLA: self.session.ticketing_href_centrale_cla,
            self.Types.CENTRALE_DD_CLA: self.session.ticketing_href_centrale_dd_cla,
            self.Types.ITEEM_CLA: self.session.ticketing_href_iteem_cla,
        }.get(self.type)

    def __str__(self):
        return f"{self.first_name} {self.last_name.upper()}"


class DataSharingLogs(models.Model):

    class Organism(models.TextChoices):
        ALUMNI = "alumni", "Centrale Lille Alumni"

    session = models.ForeignKey(RegistrationSession, related_name="+", on_delete=models.CASCADE)
    download_on = models.DateTimeField(auto_now_add=True)
    download_by = models.CharField(max_length=255, choices=Organism.choices)
