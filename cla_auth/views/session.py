
import requests

from django.contrib import auth, messages
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib.auth.models import User

from cla_auth.models import UserInfos
from cla_auth.forms.session import LoginForm
from django.utils import timezone


def login(req):
    req.session['next'] = req.GET.get('next', 'cla_public:index')

    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)
                if hasattr(user, "infos"):
                    # Check if the account lost its validation since last login
                    if user.last_login <= user.infos.valid_until <= timezone.now():
                        return redirect(req.session.get('next', 'cla_public:index'))
                return redirect(req.session.get('next', 'cla_public:index'))
            else:
                form.add_error(None, "Combinaison identifiant/mot de passe incorrecte")
    else:
        form = LoginForm()

    return render(
        req,
        'cla_auth/session/login.html',
        {
            'form': form
        }
    )


def logout(req):
    auth.logout(req)
    return redirect("cla_public:index")

