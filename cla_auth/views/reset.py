import jwt
import random

from django.views.generic import View
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.utils import timezone

from cla_auth.models import PasswordResetRequest
from cla_auth.forms.reset import ResetPasswordForm
from cla_web.utils import current_school_year


def _get_user_from_jwt(reset_jwt) -> User:
    # Retrieve jwt payload to fetch user
    try:
        jwt_payload = jwt.decode(reset_jwt, algorithms=["HS256"], options={"verify_signature": False})
    except:
        raise Http404

    user = get_object_or_404(User, pk=jwt_payload.get('pk'))
    reset_request = PasswordResetRequest.objects.get_current_reset_request(user)
    if reset_request is not None:
        # Check that the token is correct and that activation was not already done
        if reset_request.check_reset_jwt(reset_jwt):
            return user
    raise Http404


def reset(req, reset_jwt):
    user = _get_user_from_jwt(reset_jwt)

    if req.method == "POST":
        form = ResetPasswordForm(req.POST, initial={'username': user.username})
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])  # Setting user password
            user.save()

            reset_request = PasswordResetRequest.objects.get_current_reset_request(user)
            if reset_request:
                reset_request.used = True
                reset_request.save()

            return render(
                req,
                "cla_auth/reset/reset_success.html",
                {
                    'user': user
                }
            )
    else:
        form = ResetPasswordForm(initial={'username': user.username})

    return render(
        req,
        'cla_auth/reset/reset.html',
        {
            'user': user,
            'form': form,
            'reset_jwt': reset_jwt
        }
    )

