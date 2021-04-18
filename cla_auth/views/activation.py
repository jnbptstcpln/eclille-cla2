import jwt

from django.views.generic import View
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404

from cla_auth.models import UserInfos


def _get_user_from_jwt(activation_jwt):
    # Retrieve jwt payload to fetch user
    jwt_payload = jwt.decode(activation_jwt, algorithms=["HS256"], options={"verify_signature": False})
    user = get_object_or_404(User, pk=jwt_payload.get('pk'))
    if hasattr(user, 'infos'):
        # Check that the token is correct and that activation was not already done
        if user.infos.check_activation_jwt(activation_jwt) and user.infos.activated_on is None:
            return user
    raise Http404


def activate(req, activation_jwt):
    user = _get_user_from_jwt(activation_jwt)
    req.session.set('user_pk', user.pk)


def activate_rgpd(req, activation_jwt):
    user = _get_user_from_jwt(activation_jwt)


def activate_password(req, activation_jwt):
    user = _get_user_from_jwt(activation_jwt)