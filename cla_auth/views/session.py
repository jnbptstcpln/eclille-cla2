import jwt

from django.contrib import auth, messages
from django.shortcuts import render, redirect, reverse, resolve_url
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from cla_web.middlewares import StayLoggedInMiddleware
from cla_auth.models import UserInfos
from cla_auth.forms.session import LoginForm


def login(req):

    if req.user.is_authenticated:
        return redirect(req.GET.get('next', 'cla_public:index'))

    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            req.session['next'] = form.cleaned_data['redirect']
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)

                response = redirect(req.session.get('next', 'cla_public:index'))

                if hasattr(user, "infos"):
                    # Check if the account lost its validation since last login
                    if user.last_login <= user.infos.valid_until <= timezone.now() and req.session.get('validation_alert', True):
                        response = render(
                            req,
                            "cla_auth/validation/validate_alert_standalone.html",
                            {
                                'redirect': resolve_url(req.session.get('next', 'cla_public:index'))
                            }
                        )

                # Handle stay_logged_in
                if form.cleaned_data['stay_logged_in']:
                    response.set_cookie('stay_logged_in', StayLoggedInMiddleware.get_jwt(user), expires=timezone.datetime.utcnow() + timezone.timedelta(days=30))

                return response

            else:
                form.add_error(None, "Combinaison identifiant/mot de passe incorrecte")
    else:
        req.session['next'] = req.GET.get('next', 'cla_public:index')
        req.session['validation_alert'] = req.GET.get('validation_alert', '1') == '1'
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
    response = redirect("cla_public:index")
    response.delete_cookie("stay_logged_in")
    return response

