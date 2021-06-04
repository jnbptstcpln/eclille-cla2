import jwt

from django.contrib import auth, messages
from django.core.mail import send_mail
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, reverse, resolve_url, get_object_or_404
from django.utils.http import urlencode
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone

from cla_web.middlewares import StayLoggedInMiddleware
from cla_auth.models import Service, ServiceTicket, ServiceAuthorization
from cla_auth.forms.session import LoginForm, ForgotForm


def _get_service_ticket_from_jwt(ticket_jwt) -> ServiceTicket:
    # Retrieve jwt payload to fetch service ticket
    try:
        jwt_payload = jwt.decode(ticket_jwt, algorithms=["HS256"], options={"verify_signature": False})
    except:
        return None

    try:
        ticket = ServiceTicket.objects.get(pk=jwt_payload.get('pk'))
        if ticket and not ticket.used:
            return ticket
        return None
    except ServiceTicket.DoesNotExist:
        return None


def _get_error_json_response(message, status_code=400):
    return JsonResponse(
        data={
            'status': status_code,
            'success': False,
            'message': message
        },
        status=status_code
    )


def _get_success_json_response(payload, status_code=200):
    return JsonResponse(
        data={
            'status': status_code,
            'success': True,
            'payload': payload
        },
        status=status_code
    )


def authenticate(req, identifier):

    service: Service = get_object_or_404(Service, identifier=identifier)

    if not req.user.is_authenticated or (not service.auto_login and not req.session.get(f"cla_auth:{service.identifier}_login", False)):
        return login(req, identifier)

    # Check if the account has infos, i.e. it belongs to a real user
    if not hasattr(req.user, "infos"):
        return render(
            req,
            "cla_auth/service/invalid_account.html",
            {
                'service': service
            }
        )

    # Check if college user can connect to the service
    if req.user.infos.college not in service.colleges:
        return render(
            req,
            "cla_auth/service/access_denied.html",
            {
                'service': service
            }
        )

    # Check if user has given authorization to share its infos with the service
    if service.authorization_required and not service.has_user_gave_authorization(req.user):
        return authorize(req, identifier)

    # Check if the account lost its validation since last login if needed
    if service.validation_required and req.user.last_login <= req.user.infos.valid_until <= timezone.now():
        return render(
            req,
            "cla_auth/service/validate_alert_standalone.html",
            {
                'service': service,
                'redirect': resolve_url('cla_auth:service_authenticate', service.identifier)
            }
        )

    # Create ticket and redirect to the service
    ticket = service.create_ticket(req.user)
    response = redirect(f"{service.endpoint}?ticket={ticket.ticket_jwt}")
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
            user: User = auth.authenticate(req, username=username, password=password)
            if user is not None:
                auth.login(req, user)

                req.session[f"cla_auth:{service.identifier}_login"] = True
                response = redirect('cla_auth:service_authenticate', service.identifier)

                # Handle stay_logged_in
                if form.cleaned_data['stay_logged_in']:
                    response.set_cookie('stay_logged_in', StayLoggedInMiddleware.get_jwt(user), expires=timezone.datetime.utcnow() + timezone.timedelta(days=30))

                return response

            else:
                form.add_error(None, "Combinaison identifiant/mot de passe incorrecte")
    else:
        form = LoginForm()

    return render(
        req,
        'cla_auth/service/login.html',
        {
            'service': service,
            'login_message': f"Veuillez-vous connecter pour accéder au site {service.domain}",
            'form': form
        }
    )


def authorize(req, identifier):
    service: Service = get_object_or_404(Service, identifier=identifier)

    if service.has_user_gave_authorization(req.user):
        return redirect('cla_auth:service_authenticate', service.identifier)

    if req.method == 'POST':
        ServiceAuthorization.objects.create(
            service=service,
            user=req.user
        )
        return redirect("cla_auth:service_authenticate", service.identifier)

    return render(
        req,
        'cla_auth/service/authorize.html',
        {
            'service': service
        }
    )


def validate(req, identifier, ticket_jwt):
    service: Service = Service.objects.get(identifier=identifier)

    if not service:
        return _get_error_json_response("No service correspond to this identifier", status_code=404)

    ticket = _get_service_ticket_from_jwt(ticket_jwt)
    if ticket:
        if ticket.service == service:  # Check that the ticket correspond to the given service
            if ticket.check_ticket_jwt(ticket_jwt):
                ticket.used = True
                ticket.save()

                return _get_success_json_response({
                    'username': ticket.user.username,
                    'firstName': ticket.user.first_name,
                    'lastName': ticket.user.last_name,
                    'emailSchool': ticket.user.infos.email_school,
                    'cursus': ticket.user.infos.cursus,
                    'promo': ticket.user.infos.promo
                })

    return _get_error_json_response("This ticket is invalid, authentication failed")
