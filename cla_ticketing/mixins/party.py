from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect

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


class DancingPartyCollegeMixin:
    dancing_party_college_redirect = False

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.infos.college not in self.party.colleges:
            if self.dancing_party_college_redirect:
                return redirect("cla_ticketing:party_view", self.party.slug)
            return render(request, "cla_ticketing/party/unauthorized.html", self.get_context_data())
        return super().dispatch(request, *args, **kwargs)
