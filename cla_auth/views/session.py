
import requests

from django.contrib import auth, messages
from django.shortcuts import render, redirect, reverse, resolve_url
from django.conf import settings
from django.contrib.auth.models import User

from cla_auth.models import UserInfos
from cla_auth.forms.session import LoginForm
from django.utils import timezone


def login(req):

    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            req.session['next'] = form.cleaned_data['redirect']
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)
                if hasattr(user, "infos"):
                    # Check if the account lost its validation since last login
                    if user.last_login <= user.infos.valid_until <= timezone.now() or True:
                        return render(
                            req,
                            "cla_auth/validate/validate_from_login.html",
                            {
                                'redirect': resolve_url(req.session.get('next', 'cla_public:index'))
                            }
                        )
                return redirect(req.session.get('next', 'cla_public:index'))
            else:
                form.add_error(None, "Combinaison identifiant/mot de passe incorrecte")
    else:
        req.session['next'] = req.GET.get('next', 'cla_public:index')
        form = LoginForm(initial={'redirect': req.session['next']})

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

