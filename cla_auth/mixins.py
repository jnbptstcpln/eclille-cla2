import random

import jwt
from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, Http404
from django.shortcuts import render

from cla_auth.models import UserMembership


class IsContributorMixin(AccessMixin):
    is_contributor_raise_403 = False
    is_contributor_account_template = "cla_auth/exceptions/is_contributor__account.html"
    is_contributor_validation_template = "cla_auth/exceptions/is_contributor__validation.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not hasattr(request.user, 'infos'):
            if self.is_contributor_raise_403:
                raise PermissionDenied()
            else:
                return render(request, self.is_contributor_account_template)

        if not request.user.infos.is_valid():
            if self.is_contributor_raise_403:
                raise PermissionDenied()
            else:
                return render(request, self.is_contributor_validation_template, {'redirect': request.get_full_path()})

        return super().dispatch(request, *args, **kwargs)


class HasMembershipMixin(AccessMixin):
    membership: UserMembership = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not hasattr(request.user, 'infos'):
            raise PermissionDenied()

        if not request.user.infos.has_active_membership():
            raise PermissionDenied()

        self.membership = request.user.infos.get_active_membership()

        return super().dispatch(request, *args, **kwargs)


class JWTMixin:

    jwt_payload_key = "default-payload"

    @classmethod
    def generate_token(cls):
        return jwt.encode(
            payload={
                'key': cls.jwt_payload_key
            },
            key=settings.SECRET_KEY,
            algorithm="HS256"
        )

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        token = request.GET.get('token')
        try:
            jwt_payload = jwt.decode(
                token,
                key=settings.SECRET_KEY,
                algorithms=["HS256"]
            )

        except:
            raise Http404

        if jwt_payload.get('key') != self.jwt_payload_key:
            raise Http404

        return super().dispatch(request, *args, **kwargs)
