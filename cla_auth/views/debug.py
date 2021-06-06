import json
from dataclasses import dataclass
from django import forms
from django.http import HttpRequest
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from marshmallow import Schema, fields, ValidationError

from cla_auth.models import UserInfos, UserMembership


class ImportLegacyUsersView(generic.FormView):

    class Logger:

        def __init__(self):
            self.logs_success = []
            self.logs_error = []
            self._success = 0
            self._error = 0

        def success(self, message):
            self._success += 1
            self.logs_success.append({
                'type': 'success',
                'message': message
            })

        def error(self, message):
            self._error += 1
            self.logs_error.append({
                'type': 'error',
                'message': message
            })

        def has_errors(self):
            return self._error > 0

        @property
        def logs(self):
            return self.logs_error + self.logs_success

    class UserDataSchema(Schema):
        id = fields.Int()
        username = fields.Str()
        password = fields.Str()
        email = fields.Email()
        phone = fields.Str()
        email_school = fields.Email()
        first_name = fields.Str()
        last_name = fields.Str()
        promo = fields.Str()
        cursus = fields.Str()
        paid = fields.Str()
        paid_on = fields.Date(allow_none=True)
        paid_by = fields.Str()
        birthdate = fields.Date()
        created_on = fields.DateTime()
        activated_on = fields.DateTime(allow_none=True)
        valid_until = fields.DateTime(allow_none=True)

    class ProcessingException(Exception):
        def __init__(self, message):
            self.message = message

    class FileForm(forms.Form):
        users_data = forms.FileField(
            label="Fichier JSON",
            help_text="Fichier avec la structure de l'ancienne base utilisateur"
        )

    template_name = "cla_auth/debug/form.html"
    success_template_name = "cla_auth/debug/processed.html"
    form_title = "Importation utilisateurs"
    submit_label = "Importer les utilisateurs"
    form_class = FileForm

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            users_data = json.load(self.request.FILES['users_data'])
        except json.JSONDecodeError:
            form.add_error("Erreur lors de la lecture du fichier JSON, veuillez vérifier sa structure")
            return self.form_invalid(form)

        logger = self.Logger()

        for user_data in users_data:
            try:
                logger.success(self.process(user_data))
            except self.ProcessingException as e:
                logger.error(e.message)

        return render(
            self.request,
            self.success_template_name,
            context=self.get_context_data(
                logger=logger
            )
        )

    def process(self, _user_data: dict):
        try:
            user_data = self.UserDataSchema().load(_user_data)
        except ValidationError as e:
            raise self.ProcessingException(
                f"Erreur de validation sur {_user_data.get('username')} : {e.messages}"
            )

        # Check if username already exist
        if User.objects.filter(username=user_data['username']):
            raise self.ProcessingException(
                f"Un utilisateur a déjà le `username` {user_data['username']}"
            )

        user = User(
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=f"bcrypt_php${user_data['password']}" if len(user_data['password']) > 0 else "",
            email=user_data['email'],
            date_joined=user_data['created_on']
        )
        user_info = UserInfos(
            user=user,
            cursus=self.get_cursus(user_data['cursus']),
            promo=int(user_data['promo']),
            activated_on=user_data['activated_on'],
            birthdate=user_data['birthdate'],
            email_school=user_data['email_school'],
            phone=user_data['phone'],
            valid_until=user_data['valid_until'],
            account_type=UserInfos.AccountType.STUDENT
        )
        user_membership = UserMembership(
            user=user,
            amount=int(user_data['paid']),
            paid_on=user_data['paid_on'],
            paid_by=user_data['paid_by']
        )

        try:
            user.save()
            user_info.save()
            user_membership.save()
        except Exception as e:
            raise self.ProcessingException(f"Une erreur s'est produite lors de l'insertion de {user_data['username']}")

        return f"L'utilisateur {user_data.get('username')} a bien été ajouté"

    def get_cursus(self, cursus):
        return {
            "G1": UserInfos.CursusChoices.G1,
            "G1-DD-EDHEC": UserInfos.CursusChoices.G1_DD_EDHEC,
            "G1-DD-INTERNATIONAL": UserInfos.CursusChoices.G1_DD_INTERNATIONAL,
            "G1'": UserInfos.CursusChoices.G1P,
            "G1'-DD-EDHEC": UserInfos.CursusChoices.G1P_DD_EDHEC,
            "G1'-DD-INTERNATIONAL": UserInfos.CursusChoices.G1P_DD_INTERNATIONAL,
            "G2": UserInfos.CursusChoices.G2,
            "G2-DD-EDHEC": UserInfos.CursusChoices.G2_DD_EDHEC,
            "G2-DD-INTERNATIONAL": UserInfos.CursusChoices.G2_DD_INTERNATIONAL,
            "G2'": UserInfos.CursusChoices.G2P,
            "G2'-DD-EDHEC": UserInfos.CursusChoices.G2P_DD_EDHEC,
            "G2'-DD-INTERNATIONAL": UserInfos.CursusChoices.G2P_DD_INTERNATIONAL,
            "G2-CESURE-FEV": UserInfos.CursusChoices.G2_CESURE_FEV,
            "G2-CESURE-SEPT": UserInfos.CursusChoices.G2_CESURE_SEPT,
            "G3": UserInfos.CursusChoices.G3,
            "G3-DD-EDHEC": UserInfos.CursusChoices.G3_DD_EDHEC,
            "G3-GEC": UserInfos.CursusChoices.G3_GEC,
            "DD-EDHEC": UserInfos.CursusChoices.G3_DD_EDHEC,
            "DD-INTERNATIONNAL": UserInfos.CursusChoices.G3_DD_INTERNATIONAL,
            "DIPLOME": UserInfos.CursusChoices.G3_DIPLOME,
            "IE1": UserInfos.CursusChoices.IE1,
            "IE1'": UserInfos.CursusChoices.IE1P,
            "IE2": UserInfos.CursusChoices.IE2,
            "IE2'": UserInfos.CursusChoices.IE2P,
            "IE3": UserInfos.CursusChoices.IE3,
            "IE3'": UserInfos.CursusChoices.IE3P,
            "IE4": UserInfos.CursusChoices.IE4,
            "IE4'": UserInfos.CursusChoices.IE4P,
            "IE5": UserInfos.CursusChoices.IE5,
            "IE5'": UserInfos.CursusChoices.IE5P,
        }.get(cursus, None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form_title': self.form_title,
            'submit_label': self.submit_label,
        })
        return context
