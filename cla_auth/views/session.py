
import requests

from django.views.generic import View
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User

from cla_auth.models import UserInfos


class AbstractAuthView(View):
    pass


class LoginAuthView(AbstractAuthView):

    def store_next(self, req):
        req.session['next'] = req.GET.get('next', reverse('cla_public:index'))

    def get(self, req):

        self.store_next(req)

        if req.user.is_authenticated:
            return redirect(req.session.get('next', reverse('cla_public:index')))

        cla_auth_url = "https://{}/authentification/{}".format(
            settings.CLA_AUTH_HOST,
            settings.CLA_AUTH_IDENTIFIER
        )

        return redirect(cla_auth_url)


class HandleAuthView(AbstractAuthView):

    def get(self, req):

        if req.user.is_authenticated:
            return redirect(req.session.get('next', reverse('cla_public:index')))

        ticket = req.GET.get('ticket')

        cla_auth_url = "https://{}/authentification/{}/{}".format(
            settings.CLA_AUTH_HOST,
            settings.CLA_AUTH_IDENTIFIER,
            requests.utils.quote(ticket)
        )

        rep = requests.get(cla_auth_url)

        try:
            auth = rep.json()
        except Exception as e:
            return render(req, "cla_auth/error.html")

        if auth.get('success'):
            payload = auth.get('payload')
            username = payload.get('username')

            try:
                user = User.objects.get(username=username)

                # Update user's infos
                user.first_name = payload.get('firstName')
                user.last_name = payload.get('lastName')
                user.email_name = payload.get('emailSchool')
                user.save()
                user.infos.promo = payload.get('promo')
                user.infos.cursus = payload.get('cursus')
                user.infos.save()

            except User.DoesNotExist:
                # Create the user entity
                user = User.objects.create(
                    username=payload.get('username'),
                    first_name=payload.get('firstName'),
                    last_name=payload.get('lastName'),
                    email=payload.get('emailSchool'),
                    is_active=True,
                    password=""
                )
                user.infos = UserInfos.objects.create(user=user, promo=payload.get('promo'), cursus=payload.get('cursus'))

            login(req, user)

            return redirect(req.session.get('next', reverse('cla_public:index')))

        return render(req, "cla_auth/error.html")


class LogoutAuthView(AbstractAuthView):

    def get(self, req):
        logout(req)
