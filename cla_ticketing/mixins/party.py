from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View, CreateView, TemplateView

from cla_auth.mixins import IsContributorMixin
from cla_ticketing.models import DancingParty, DancingPartyRegistration


class DancingPartyRegistrationMixin:
    party: DancingParty = None
    registration_self: DancingPartyRegistration = None
    registration_friend: DancingPartyRegistration = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.party = get_object_or_404(DancingParty, slug=kwargs.pop("party_slug", None))
        if request.user.is_authenticated:
            self.registration_self = self.party.registrations.filter(user=request.user).first()
            self.registration_friend = self.party.registrations.filter(guarantor=request.user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'party': self.party,
            'registration_self': self.registration_self,
            'registration_friend': self.registration_friend
        })
        return context
