import jwt
import random

from django.views.generic import View
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.utils import timezone

from cla_auth.models import UserInfos
from cla_auth.forms.activation import ActivationRgpdForm, ActivationPasswordForm
from cla_web.utils import current_school_year


def _get_user_from_jwt(activation_jwt) -> User:
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

    # Reset activation related session's content
    req.session['rgpd_agreement'] = False

    return render(
        req,
        'cla_auth/activation/activate.html',
        {
            'user': user
        }
    )


def activate_rgpd(req, activation_jwt):
    user = _get_user_from_jwt(activation_jwt)

    if req.method == "POST":
        form = ActivationRgpdForm(req.POST)
        if form.is_valid():
            req.session['rgpd_agreement'] = True
            return redirect("cla_auth:activate_password", user.infos.activation_jwt)
    else:
        form = ActivationRgpdForm()

    return render(
        req,
        'cla_auth/activation/activate_rgpd.html',
        {
            'form': form,
            'user': user
        }
    )


def activate_password(req, activation_jwt):
    user = _get_user_from_jwt(activation_jwt)

    if not req.session.get('rgpd_agreement', False):
        return redirect("cla_auth:activate_rgpd", user.infos.activation_jwt)

    if req.method == "POST":
        form = ActivationPasswordForm(req.POST, initial={'username': user.username})
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])  # Setting user password
            user.save()

            user.infos.activated_on = timezone.now()  # Saving the activation
            user.infos.valid_until = timezone.datetime(year=current_school_year()+1, month=9, day=random.randint(10, 25))  # Setting the validation
            user.infos.save()

            return render(
                req,
                "cla_auth/activation/activate_success.html",
                {
                    'user': user
                }
            )
    else:
        form = ActivationPasswordForm(initial={'username': user.username})

    return render(
        req,
        'cla_auth/activation/activate_password.html',
        {
            'form': form,
            'user': user
        }
    )
