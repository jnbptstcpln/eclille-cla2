import re
import os
import uuid
import jwt

from cla_web.utils import random_six_digits

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.text import slugify
from django_resized import ResizedImageField
from multiselectfield import MultiSelectField

from cla_web.utils import current_school_year


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s-%s.%s" % (slugify(instance.name), uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def picture(cls, instance, filename):
        return cls._path(instance, ["cla_auth", "user", "picture"], filename)


class UserInfos(models.Model):
    """
        The UserInfo model extends user by adding new properties
    """

    class Meta:
        verbose_name = "Information"
        permissions = (
            ('manage_user_activation', "Accès au processus d'activation des comptes"),
            ('manage_user_validation', "Accès au processus de validation des comptes"),
            ('manage_user_password', "Accès au processus de réinitialisation des mots de passes"),
            ('autocomplete_user', "Accès à la fonctionnalité d'autocomplétion sur les champs utilisateur"),
        )

    class AccountType(models.TextChoices):
        STUDENT = 'student', "Étudiant"
        SCHOOL = 'school', 'Personnel de l\'école'
        OTHER = 'other', 'Autre'

    class Colleges(models.TextChoices):
        G1 = 'g1', 'G1'
        G2 = 'g2', 'G2'
        G3 = 'g3', 'G3'
        ALUMNI_CENTRALE = 'alumni-centrale', 'Diplomé de Centrale'
        IE1_IE2 = 'ie1/ie2', 'IE1/IE2'
        IE3 = 'ie3', 'IE3'
        IE4 = 'ie4', 'IE4'
        IE5 = 'ie5', 'IE5'
        ALUMNI_ITEEM = 'alumni-iteem', 'Diplomé de l\'ITEEM'

    class CursusChoices(models.TextChoices):

        # # # # # # # # # #
        # CURSUS CENTRALE #
        # # # # # # # # # #

        G1 = "G1", "G1"
        G1_DD_EDHEC = "G1-DD-EDHEC", "G1 en double diplôme avec EDHEC"
        G1_DD_INTERNATIONAL = "G1-DD-INTERNATIONAL", "G1 en double diplôme international"
        G1P = "G1'", "G1'"
        G1P_DD_EDHEC = "G1'-DD-EDHEC", "G1' en double diplôme EDHEC"
        G1P_DD_INTERNATIONAL = "G1'-DD-INTERNATIONAL", "G1' en double diplôme international"

        G2 = "G2", "G2"
        G2_DD_EDHEC = "G2-DD-EDHEC", "G2 en double diplôme avec l'EDHEC"
        G2_DD_INTERNATIONAL = "G2-DD-INTERNATIONAL", "G2 en double diplôme international"
        G2_CESURE_FEV = "G2-CESURE-FEV", "G2 en césure février/février"
        G2_CESURE_SEPT = "G2-CESURE-SEPT", "G2 en année sabatique"

        G2P = "G2'", "G2'"
        G2P_DD_EDHEC = "G2'-DD-EDHEC", "G2' en double diplôme avec l'EDHEC"
        G2P_DD_INTERNATIONAL = "G2'-DD-INTERNATIONAL", "G2' en double diplôme international"
        G2P_CESURE_FEV = "G2'-CESURE-FEV", "G2 en césure février/février"
        G2P_CESURE_SEPT = "G2'-CESURE-SEPT", "G2 en année sabatique"

        G3 = "G3", "G3"
        G3_GEC = "G3-GEC", "G3 en mobilité intercentrale"
        G3_DD_EDHEC = "G3-DD-EDHEC", "Double diplôme avec l'EDHEC"
        G3_DD_SCIENCESPO = "G3-DD-SCIENCESPO", "Double diplôme avec Sciences Po"
        G3_DD_INTERNATIONAL = "DD-INTERNATIONAL", "Double diplôme internationnal"
        G3_DD_FRANCE = "DD-FRANCE", "Double diplôme en France"

        G3_DIPLOME_DD_EDHEC = "G3-DIPLOME-DD-EDHEC", "Diplomé DD EDHEC"
        G3_DIPLOME_DD_INTERNATIONAL = "G3-DIPLOME-DD-INTERNATIONAL", "Diplomé DD Internationnal"

        G3_DIPLOME = "G3-DIPLOME", "Diplomé de Centrale"

        # # # # # # # # #
        # CURSUS  ITEEM #
        # # # # # # # # #

        IE1 = "IE1", "IE1"
        IE1P = "IE1P", "IE1'"

        IE2 = "IE2", "IE2"
        IE2P = "IE2P", "IE2'"

        IE3 = "IE3", "IE3"
        IE3P = "IE3P", "IE3'"

        IE4 = "IE4", "IE4"
        IE4P = "IE4P", "IE4'"

        IE5 = "IE5", "IE5"
        IE5P = "IE5P", "IE5'"

        IE5_DIPLOME = "IE5-DIPLOME", 'Diplomé de l\ITEEM'

        # # # # # # # # #
        # CURSUS  AUTRE #
        # # # # # # # # #
        AUTRE = "Autre", "Autre cursus"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="infos", to_field="username")
    email_school = models.EmailField(null=False, verbose_name="Adresse mail de l'école")
    account_type = models.CharField(max_length=10, choices=AccountType.choices, default=AccountType.STUDENT, verbose_name="Type de compte")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    cursus = models.CharField(max_length=100, null=True, choices=CursusChoices.choices, verbose_name="Cursus")
    promo = models.PositiveIntegerField(verbose_name="Promotion (lors de l'arrivée à Centrale)")
    birthdate = models.DateField(verbose_name="Date de naissance")
    activated_on = models.DateTimeField(verbose_name="Date d'activation du compte", null=True)
    valid_until = models.DateTimeField(verbose_name="Compte valide jusqu'au", null=True)
    original_school = models.CharField(max_length=255, null=True, verbose_name="École/université d'origine")
    picture = ResizedImageField(
        verbose_name="Photo de profil",
        upload_to=FilePath.picture,
        size=[500, 500],
        quality=90,
        force_format="JPEG",
        keep_meta=False,
        null=True,
        blank=True
    )

    def is_from_centrale(self):
        return re.match(r'^G\d.*', self.cursus)

    def is_from_iteem(self):
        return re.match(r'^IE\d.*', self.cursus)

    def is_activated(self):
        return self.activated_on is not None

    def is_valid(self):
        return self.valid_until is not None and self.valid_until > timezone.now()

    @property
    def activation_jwt(self):
        return jwt.encode(
            payload={
                'pk': self.user.pk
            },
            key=f"{settings.SECRET_KEY}-{self.user.username}",
            algorithm="HS256"
        )

    def check_activation_jwt(self, token):
        try:
            payload = jwt.decode(
                jwt=token,
                key=f"{settings.SECRET_KEY}-{self.user.username}",
                algorithms=["HS256"]
            )
            return True
        except:
            return False

    @property
    def validation_request(self):
        validation_request, created = ValidationRequest.objects.get_or_create(
            user=self.user,
            email_school=self.email_school,
            used=False
        )
        return validation_request

    @property
    def validation_code(self):
        return self.validation_request.code

    @property
    def reset_request(self):
        return PasswordResetRequest.objects.get_current_reset_request(self.user)

    @property
    def college(self):
        if self.promo <= current_school_year() and self.valid_until < timezone.now():
            return self.Colleges.ALUMNI_CENTRALE if self.is_from_centrale() else self.Colleges.ALUMNI_ITEEM
        elif self.promo <= current_school_year() + 1:
            return self.Colleges.G3 if self.is_from_centrale() else self.Colleges.IE5
        elif self.promo == current_school_year() + 2:
            return self.Colleges.G2 if self.is_from_centrale() else self.Colleges.IE4
        elif self.promo == current_school_year() + 3:
            return self.Colleges.G1 if self.is_from_centrale() else self.Colleges.IE3
        elif self.promo == current_school_year() + 4:
            return self.Colleges.IE1_IE2
        elif self.promo == current_school_year() + 5:
            return self.Colleges.IE1_IE2

    @property
    def next_cursus_choices(self):
        if self.cursus == self.CursusChoices.G1:
            class NextCursusChoices(models.TextChoices):
                G1P = self.CursusChoices.G1P.value, self.CursusChoices.G1P.label
                G2 = self.CursusChoices.G2.value, self.CursusChoices.G2.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G1_DD_EDHEC:
            class NextCursusChoices(models.TextChoices):
                G1P_DD_EDHEC = self.CursusChoices.G1P_DD_EDHEC.value, self.CursusChoices.G1P_DD_EDHEC.label
                G2_DD_EDHEC = self.CursusChoices.G2_DD_EDHEC.value, self.CursusChoices.G2_DD_EDHEC.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G1_DD_INTERNATIONAL:
            class NextCursusChoices(models.TextChoices):
                G1P_DD_INTERNATIONAL = self.CursusChoices.G1P_DD_INTERNATIONAL.value, self.CursusChoices.G1P_DD_INTERNATIONAL.label
                G2_DD_INTERNATIONAL = self.CursusChoices.G2_DD_INTERNATIONAL.value, self.CursusChoices.G2_DD_INTERNATIONAL.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G1P:
            class NextCursusChoices(models.TextChoices):
                G2 = self.CursusChoices.G2.value, self.CursusChoices.G2.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G1P_DD_EDHEC:
            class NextCursusChoices(models.TextChoices):
                G2_DD_EDHEC = self.CursusChoices.G2_DD_EDHEC.value, self.CursusChoices.G2_DD_EDHEC.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G1P_DD_INTERNATIONAL:
            class NextCursusChoices(models.TextChoices):
                G1P_DD_INTERNATIONAL = self.CursusChoices.G1P_DD_INTERNATIONAL.value, self.CursusChoices.G1P_DD_INTERNATIONAL.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.G2, self.CursusChoices.G2P}:
            class NextCursusChoices(models.TextChoices):
                G2P = self.CursusChoices.G2P.value, self.CursusChoices.G2P.label
                G3 = self.CursusChoices.G3.value, self.CursusChoices.G3.label
                G3_DD_EDHEC = self.CursusChoices.G3_DD_EDHEC.value, self.CursusChoices.G3_DD_EDHEC.label
                G3_DD_SCIENCESPO = self.CursusChoices.G3_DD_SCIENCESPO.value, self.CursusChoices.G3_DD_SCIENCESPO.label
                G3_DD_FRANCE = self.CursusChoices.G3_DD_FRANCE.value, self.CursusChoices.G3_DD_FRANCE.label
                G3_DD_INTERNATIONAL = self.CursusChoices.G3_DD_INTERNATIONAL.value, self.CursusChoices.G3_DD_INTERNATIONAL.label
                G2_CESURE_FEV = self.CursusChoices.G2_CESURE_FEV.value, self.CursusChoices.G2_CESURE_FEV.label
                G2_CESURE_SEPT = self.CursusChoices.G2_CESURE_SEPT.value, self.CursusChoices.G2_CESURE_SEPT.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.G2_DD_EDHEC, self.CursusChoices.G2P_DD_EDHEC}:
            class NextCursusChoices(models.TextChoices):
                G2P_DD_EDHEC = self.CursusChoices.G2P_DD_EDHEC.value, self.CursusChoices.G2P_DD_EDHEC.label
                G3_DIPLOME_DD_EDHEC = self.CursusChoices.G3_DIPLOME_DD_EDHEC.value, self.CursusChoices.G3_DIPLOME_DD_EDHEC.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.G2_DD_INTERNATIONAL, self.CursusChoices.G2P_DD_INTERNATIONAL}:
            class NextCursusChoices(models.TextChoices):
                G2P_DD_INTERNATIONAL = self.CursusChoices.G2P_DD_INTERNATIONAL.value, self.CursusChoices.G2P_DD_INTERNATIONAL.label
                G3_DIPLOME_DD_INTERNATIONAL = self.CursusChoices.G3_DIPLOME_DD_INTERNATIONAL.value, self.CursusChoices.G3_DIPLOME_DD_INTERNATIONAL.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.G2_CESURE_FEV, self.CursusChoices.G2_CESURE_SEPT}:
            class NextCursusChoices(models.TextChoices):
                G2P = self.CursusChoices.G2P.value, self.CursusChoices.G2P.label
                G3 = self.CursusChoices.G3.value, self.CursusChoices.G3.label
                G3_DD_EDHEC = self.CursusChoices.G3_DD_EDHEC.value, self.CursusChoices.G3_DD_EDHEC.label
                G3_DD_SCIENCESPO = self.CursusChoices.G3_DD_SCIENCESPO.value, self.CursusChoices.G3_DD_SCIENCESPO.label
                G3_DD_FRANCE = self.CursusChoices.G3_DD_FRANCE.value, self.CursusChoices.G3_DD_FRANCE.label
                G3_DD_INTERNATIONAL = self.CursusChoices.G3_DD_INTERNATIONAL.value, self.CursusChoices.G3_DD_INTERNATIONAL.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G3:
            class NextCursusChoices(models.TextChoices):
                G3 = self.CursusChoices.G3.value, self.CursusChoices.G3.label
                G3_DIPLOME = self.CursusChoices.G3_DIPLOME.value, self.CursusChoices.G3_DIPLOME.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G3_DD_EDHEC:
            class NextCursusChoices(models.TextChoices):
                G3_DD_EDHEC = self.CursusChoices.G3_DD_EDHEC.value, self.CursusChoices.G3_DD_EDHEC.label
                G3_DIPLOME = self.CursusChoices.G3_DIPLOME.value, self.CursusChoices.G3_DIPLOME.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G3_DD_SCIENCESPO:
            class NextCursusChoices(models.TextChoices):
                G3_DD_SCIENCESPO = self.CursusChoices.G3_DD_SCIENCESPO.value, self.CursusChoices.G3_DD_SCIENCESPO.label
                G3_DIPLOME = self.CursusChoices.G3_DIPLOME.value, self.CursusChoices.G3_DIPLOME.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G3_DD_INTERNATIONAL:
            class NextCursusChoices(models.TextChoices):
                G3_DD_INTERNATIONAL = self.CursusChoices.G3_DD_INTERNATIONAL.value, self.CursusChoices.G3_DD_INTERNATIONAL.label
                G3_DIPLOME = self.CursusChoices.G3_DIPLOME.value, self.CursusChoices.G3_DIPLOME.label

            return NextCursusChoices

        elif self.cursus == self.CursusChoices.G3_DD_FRANCE:
            class NextCursusChoices(models.TextChoices):
                G3_DD_FRANCE = self.CursusChoices.G3_DD_FRANCE.value, self.CursusChoices.G3_DD_FRANCE.label
                G3_DIPLOME = self.CursusChoices.G3_DIPLOME.value, self.CursusChoices.G3_DIPLOME.label

            return NextCursusChoices

        if self.cursus in {self.CursusChoices.IE1, self.CursusChoices.IE1P}:
            class NextCursusChoices(models.TextChoices):
                IE2 = self.CursusChoices.IE2.value, self.CursusChoices.IE2.label
                IE1P = self.CursusChoices.IE1P.value, self.CursusChoices.IE1P.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.IE2, self.CursusChoices.IE2P}:
            class NextCursusChoices(models.TextChoices):
                IE3 = self.CursusChoices.IE3.value, self.CursusChoices.IE3.label
                IE2P = self.CursusChoices.IE2P.value, self.CursusChoices.IE2P.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.IE3, self.CursusChoices.IE3P}:
            class NextCursusChoices(models.TextChoices):
                IE4 = self.CursusChoices.IE4.value, self.CursusChoices.IE4.label
                IE3P = self.CursusChoices.IE3P.value, self.CursusChoices.IE3P.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.IE4, self.CursusChoices.IE4P}:
            class NextCursusChoices(models.TextChoices):
                IE5 = self.CursusChoices.IE5.value, self.CursusChoices.IE5.label
                IE4P = self.CursusChoices.IE4P.value, self.CursusChoices.IE4P.label

            return NextCursusChoices

        elif self.cursus in {self.CursusChoices.IE5, self.CursusChoices.IE5}:
            class NextCursusChoices(models.TextChoices):
                IE5 = self.CursusChoices.IE5.value, self.CursusChoices.IE5.label
                IE5_DIPLOME = self.CursusChoices.IE5_DIPLOME.value, self.CursusChoices.IE5_DIPLOME.label

            return NextCursusChoices

        # Fallback next cursus choices
        class NextCursusChoices(models.TextChoices):
            AUTRE = self.CursusChoices.AUTRE.value, self.CursusChoices.AUTRE.label

        return NextCursusChoices

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.get_account_type_display()})"


class PasswordResetRequestManager(models.Manager):

    def get_current_reset_request(self, user):
        """
        Reset request are only valid for 24h hours
        """
        return self.filter(user=user, used=False, created_on__gte=timezone.now() - timezone.timedelta(hours=24)).last()

    def get_or_create_reset_request(self, user, count_attempt=True):
        reset_request = self.get_current_reset_request(user)
        if reset_request:
            if count_attempt:
                reset_request.attempt += 1  # Saving the attempt
                reset_request.save()
            return reset_request
        else:
            return self.create(
                user=user,
                email=user.email
            )


class PasswordResetRequest(models.Model):

    class Meta:
        ordering = "created_on",

    objects = PasswordResetRequestManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    email = models.EmailField()
    created_on = models.DateTimeField(auto_now=True)
    used = models.BooleanField(default=False)
    attempt = models.IntegerField(default=0)

    def get_reset_jwt(self, exp=True):
        payload = {'pk': self.user.pk}
        if exp:
            payload['exp'] = timezone.datetime.utcnow() + timezone.timedelta(minutes=60)  # Token is valid for 60 minutes

        return jwt.encode(
            payload=payload,
            key=f"{settings.SECRET_KEY}-{self.user.password}-{self.user.date_joined.time()}",
            algorithm="HS256"
        )

    def check_reset_jwt(self, token):
        try:
            payload = jwt.decode(
                jwt=token,
                key=f"{settings.SECRET_KEY}-{self.user.password}-{self.user.date_joined.time()}",
                algorithms=["HS256"]
            )
            return True
        except:
            return False


class ValidationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    email_school = models.EmailField()
    created_on = models.DateTimeField(auto_now=True)
    sent_on = models.DateTimeField(null=True)
    code = models.IntegerField(default=random_six_digits)
    used = models.BooleanField(default=False)
    attempt = models.IntegerField(default=0)


class UserMembership(models.Model):

    class Meta:
        verbose_name = "Cotisation"

    class MeanOfPayment(models.TextChoices):
        PUMPKIN = 'pumpkin', 'Pumpkin'
        CHECK = 'check', 'Chèque'
        CASH = 'cash', 'Liquide'
        TRANSFER = 'transfer', 'Virement'
        CARD = 'card', 'Carte bancaire'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="membership", to_field="username")
    amount = models.PositiveIntegerField(verbose_name="Montant de la cotisation", blank=True)
    paid_on = models.DateField(verbose_name="Date de paiement", null=True, blank=True)
    paid_by = models.CharField(max_length=100, choices=MeanOfPayment.choices, verbose_name="Moyen de paiement", blank=True)
    refunded = models.BooleanField(default=False, blank=True, verbose_name="La cotisation a été remboursée")
    refunded_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name="Montant remboursé")
    refunded_on = models.DateField(null=True, blank=True, verbose_name="Date du remboursement")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Service(models.Model):

    class Meta:
        verbose_name = "Service"
        ordering = "name",

    identifier = models.CharField(max_length=100, verbose_name="Identifiant du service", unique=True)
    name = models.CharField(max_length=100, verbose_name="Nom du service")
    domain = models.CharField(max_length=250, verbose_name="Nom de domaine du service")
    endpoint = models.CharField(max_length=250, verbose_name="Endpoint du service")
    validation_required = models.BooleanField(default=True, verbose_name="La validation du compte est requise pour se connecter (permet de s'assurer que l'utilisateur est encore cotisant)")
    authorization_required = models.BooleanField(default=True, verbose_name="L'utilisateur doit approuver le partage d'informations lors de la première utilisation")
    colleges = MultiSelectField(choices=UserInfos.Colleges.choices, verbose_name="Collèges autorisés à se connecter", blank=True)
    auto_login = models.BooleanField(default=True, verbose_name="Connexion automatique")

    def has_user_gave_authorization(self, user: User):
        return ServiceAuthorization.objects.filter(service=self, user=user).count() > 0

    def create_ticket(self, user):
        return ServiceTicket.objects.create(
            user=user,
            service=self
        )

    def __str__(self):
        return self.name


class ServiceAuthorization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", to_field="username")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="+", to_field="identifier")
    created_on = models.DateTimeField(auto_now=True)


class ServiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", to_field="username")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="tickets", to_field="identifier")
    created_on = models.DateTimeField(auto_now=True)
    used = models.BooleanField(default=False)

    @property
    def ticket_jwt(self):
        return jwt.encode(
            payload={
                'pk': self.pk,
                'exp': timezone.datetime.utcnow() + timezone.timedelta(seconds=15)  # Token is valid for 15 seconds
            },
            key=f"{settings.SECRET_KEY}-{self.user.username}",
            algorithm="HS256"
        )

    def check_ticket_jwt(self, token):
        if self.used:
            return False
        else:
            try:
                payload = jwt.decode(
                    jwt=token,
                    key=f"{settings.SECRET_KEY}-{self.user.username}",
                    algorithms=["HS256"]
                )
                return True
            except:
                return False
