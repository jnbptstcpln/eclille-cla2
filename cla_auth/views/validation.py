import random

import jwt

from django.views.generic import View
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from cla_auth.models import UserInfos
from cla_auth.forms.validation import ValidationForm
from cla_web.utils import current_school_year


@login_required()
def validate(req):
    user: User = req.user

    # Only deal with non management users
    if not hasattr(user, 'infos'):
        return redirect(req.session.get('next', 'cla_public:index'))

    # Redirect the user if its account is validated
    if user.infos.valid_until > timezone.now():
        return redirect(req.session.get('next', 'cla_public:index'))

    validation_request = user.infos.validation_request

    if req.method == "POST":
        form = ValidationForm(req.POST, user=req.user)
        if form.is_valid():
            # Set valid_until to a random date between 10th September and 25th September
            # The lower boundaries (10/09) is set to not create to much problems on the first "soirée dansante"
            # With people who wouldn't get their place because of account validation delay
            user.infos.valid_until = timezone.datetime(year=current_school_year()+1, month=9, day=random.randint(10, 25))
            user.infos.save()

            return render(
                req,
                "cla_auth/validation/validate_success_standalone.html",
                {
                    'redirect': resolve_url(req.session.get('next', 'cla_public:index'))
                }
            )
    else:
        # Only send the email when it has not been sent or has been sent more than 1 hour ago
        if validation_request.sent_on is None or validation_request.sent_on + timezone.timedelta(hours=1) > timezone.now():
            send_mail(
                subject='[CLA] Activation de votre compte',
                from_email=settings.EMAIL_HOST_FROM,
                recipient_list=[user.infos.email_school],
                message=f"Voici le code à indiquer pour valider votre compte : {validation_request.code}",
                html_message=render_to_string(
                    'cla_auth/validation/mail.html',
                    {
                        'site_href': f"https://{settings.ALLOWED_HOSTS[0]}",
                        'validation_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_auth:validate')}",
                        'validation_request': validation_request,
                    }
                ),
            )
            validation_request.sent_on = timezone.now()
            validation_request.save()

        form = ValidationForm(user=req.user)

    return render(
        req,
        'cla_auth/validation/validate_standalone.html',
        {
            'form': form,
            'redirect': resolve_url(req.session.get('next', 'cla_public:index'))
        }
    )
