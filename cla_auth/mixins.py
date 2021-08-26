from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from django.http import HttpRequest


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
