import jwt

from django.contrib import auth, messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, resolve_url, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone

from cla_web.middlewares import StayLoggedInMiddleware
from cla_auth.models import Service, ServiceTicket
from cla_auth.forms.session import LoginForm, ForgotForm


def authenticate(req, identifier):

    service: Service = get_object_or_404(Service, identifier=identifier)

    if not req.user.is_authenticated or (not service.auto_login and not req.session.get(f"cla_auth:{service.identifier}_login", False)):
        return redirect('cla_auth:service_login', service.identifier)

    if hasattr(req.user, "infos"):
        # Check if the account lost its validation since last login
        if req.user.last_login <= req.user.infos.valid_until <= timezone.now() and req.session.get('validation_alert', True):
            response = render(
                req,
                "cla_auth/validation/validate_alert_standalone.html",
                {
                    'redirect': resolve_url(req.session.get('next', 'cla_public:index'))
                }
            )

    response = redirect("")
    req.session[f"cla_auth:{service.identifier}_login"] = False  # Reset session login before redirect to service

    return response


def login(req, identifier):
    service: Service = get_object_or_404(Service, identifier=identifier)

    if req.user.is_authenticated and service.auto_login:
        return redirect('cla_auth:service_authenticate', service.identifier)

    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            req.session['next'] = form.cleaned_data['redirect']
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)

                req.session[f"cla_auth:{service.identifier}_login"] = True
                response = redirect('cla_auth:service_authenticate')

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

    pass


def validate(req, identifier, ticket):
    service: Service = get_object_or_404(Service, identifier=identifier)

    if req.user.is_authenticated:
        return redirect('cla_public:index')



