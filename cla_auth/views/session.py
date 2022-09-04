import jwt

from django.contrib import auth, messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, resolve_url
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from cla_web.middlewares import StayLoggedInMiddleware
from cla_auth.models import PasswordResetRequest
from cla_auth.forms.session import LoginForm, ForgotForm
from cla_web.notification import send_generic_email


@csrf_protect
def login(req):
    if req.user.is_authenticated:
        return redirect(req.GET.get('next', 'cla_member:lobby'))

    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            req.session['next'] = form.cleaned_data['redirect']
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)

                response = redirect(req.session.get('next', 'cla_member:lobby'))

                if hasattr(user, "infos"):
                    # Check if the account lost its validation since last login
                    if user.infos.valid_until is not None:
                        if user.last_login <= user.infos.valid_until <= timezone.now() and req.session.get('validation_alert', True):
                            response = render(
                                req,
                                "cla_auth/validation/validate_alert_standalone.html",
                                {
                                    'redirect': resolve_url(req.session.get('next', 'cla_member:lobby'))
                                }
                            )

                # Handle stay_logged_in
                if form.cleaned_data['stay_logged_in']:
                    response.set_cookie('stay_logged_in', StayLoggedInMiddleware.get_jwt(user), expires=timezone.datetime.utcnow() + timezone.timedelta(days=30))

                return response

            else:
                form.add_error(None, "Combinaison identifiant/mot de passe incorrecte")
    else:
        req.session['next'] = req.GET.get('next', 'cla_member:lobby')
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
        return redirect('cla_member:lobby')

    return render(
        req,
        'cla_auth/session/forgot.html'
    )


def forgot_username(req):
    if req.user.is_authenticated:
        return redirect('cla_member:lobby')

    username = None
    server_error = False
    if req.method == "POST":
        form = ForgotForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.count() == 1:
                username = User.objects.get(email=email).username
            elif users.count() > 1:
                server_error = True
                send_generic_email(
                    f"Plusieurs utilisateurs pour {email}",
                    f"Lors de l'exécution de la fonction \"J'ai oublié mon identifiant\", l'adresse email {email} a retourné plusieurs comptes utilisateur. La personne concernée a été invitée à contacter cla@centralelille.fr et des actions doivent être prises pour préserver l'unicité utilisateur/email."
                )
    else:
        form = ForgotForm()

    return render(
        req,
        'cla_auth/session/forgot_username.html',
        {
            'username': username,
            'form': form,
            'server_error': server_error
        }
    )


def forgot_password(req):
    if req.user.is_authenticated:
        return redirect('cla_member:lobby')

    error = None
    warning = None
    success = None
    server_error = False

    if req.method == "POST":
        form = ForgotForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            users = User.objects.filter(email=email)
            if users.count() == 1:
                reset_req: PasswordResetRequest = PasswordResetRequest.objects.get_or_create_reset_request(user=user)
                if reset_req.attempt < 3:  # Send reset email if less than 3 attempts were made
                    try:
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
                    except Exception as e:
                        send_mail(
                            subject=f'[RESET] Erreur lors de l\'envoie à {user.email}',
                            from_email=settings.EMAIL_HOST_FROM,
                            recipient_list=[settings.EMAIL_HOST_FROM],
                            message=f"Une erreur s'est produite lors de l'envoi du mail de réinitilisation de mot de passe à {user.email} : {e}"
                        )
                    success = True
                else:
                    warning = True
            elif users.count() > 1:
                server_error = True
                send_generic_email(
                    f"Plusieurs utilisateurs pour {email}",
                    f"Lors de l'exécution de la fonction \"J'ai oublié mon mot de passe\", l'adresse email {email} a retourné plusieurs comptes utilisateur. La personne concernée a été invitée à contacter cla@centralelille.fr et des actions doivent être prises pour préserver l'unicité utilisateur/email."
                )

    else:
        form = ForgotForm()

    return render(
        req,
        'cla_auth/session/forgot_password.html',
        {
            'form': form,
            'error': error,
            'warning': warning,
            'success': success,
            'server_error': server_error
        }
    )


def logout(req):
    auth.logout(req)
    response = redirect("cla_public:index")
    response.delete_cookie("stay_logged_in")
    return response
