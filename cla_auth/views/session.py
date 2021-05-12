import jwt

from django.contrib import auth, messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, resolve_url
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone

from cla_web.middlewares import StayLoggedInMiddleware
from cla_auth.models import PasswordResetRequest
from cla_auth.forms.session import LoginForm, ForgotForm


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


def forgot(req):

    if req.user.is_authenticated:
        return redirect('cla_public:index')

    return render(
        req,
        'cla_auth/session/forgot.html'
    )


def forgot_username(req):

    if req.user.is_authenticated:
        return redirect('cla_public:index')

    if req.method == "POST":
        form = ForgotForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                username = User.objects.get(email=email).username
            except User.DoesNotExist:
                pass
    else:
        form = ForgotForm()
        username = None

    return render(
        req,
        'cla_auth/session/forgot_username.html',
        {
            'username': username,
            'form': form
        }
    )


def forgot_password(req):

    if req.user.is_authenticated:
        return redirect('cla_public:index')

    error = None
    warning = None
    success = None

    if req.method == "POST":
        form = ForgotForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                reset_req: PasswordResetRequest = PasswordResetRequest.objects.get_or_create_reset_request(user=user)
                if reset_req.attempt < 3:  # Send reset email if less than 3 attempts were made
                    send_mail(
                        subject='[CLA] Réinitialiser votre mot de passe',
                        from_email=settings.EMAIL_HOST_FROM,
                        recipient_list=[user.email],
                        message="Réinitialiser le mot de passe de votre compte CLA",
                        html_message=render_to_string(
                            'cla_auth/reset/mail.html',
                            {
                                'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                                'reset_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_auth:reset', reset_req.get_reset_jwt())}",
                            }
                        ),
                    )
                    success = True
                else:
                    warning = True

            except User.DoesNotExist:
                pass
    else:
        form = ForgotForm()

    return render(
        req,
        'cla_auth/session/forgot_password.html',
        {
            'form': form,
            'error': error,
            'warning': warning,
            'success': success
        }
    )


def logout(req):
    auth.logout(req)
    response = redirect("cla_public:index")
    response.delete_cookie("stay_logged_in")
    return response

