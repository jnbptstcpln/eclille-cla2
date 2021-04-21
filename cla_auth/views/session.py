
import requests

from django.views.generic import View
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User

from cla_auth.models import UserInfos
from cla_auth.forms.session import LoginForm


def login(req):
    req.session['next'] = req.GET.get('next', reverse('cla_public:index'))

    if req.method == 'POST':
        form = LoginForm(req.POST)
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

