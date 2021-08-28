import csv

from django.db.models import Q
from django.views.generic import TemplateView
from django.contrib import admin, messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponseNotAllowed, Http404, HttpResponse
from django.utils import timezone

from cla_ticketing.models import Event, DancingParty, DancingPartyRegistration


from cla_member.mixins import ClaMemberModuleMixin


class IndexView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_member/lobby/index.html"
    cla_member_active_section = 'index'

    def get_opened_events(self):
        events = Event.objects.filter(
            registration_starts_on__lte=timezone.now(),
            registration_ends_on__gt=timezone.now(),
        )
        return [
            event for event in events if self.request.user.infos.college in event.colleges
        ]

    def get_opened_parties(self):
        parties = DancingParty.objects.filter(
            registration_starts_on__lte=timezone.now(),
            registration_ends_on__gt=timezone.now(),
        )
        return [
            party for party in parties if self.request.user.infos.college in party.colleges
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'events': self.get_opened_events(),
            'parties': self.get_opened_parties()
        })
        return context


class TicketingView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_member/lobby/ticketing.html"
    cla_member_active_section = 'ticketing'

    def get_staffed_upcoming_parties(self):
        parties = DancingParty.objects.filter(
            event_starts_on__lte=(timezone.now()+timezone.timedelta(hours=3)),
            event_ends_on__gte=(timezone.now()-timezone.timedelta(hours=3)),
        )
        if self.request.user.has_perm("cla_ticketing.add_dancingparty"):
            return parties
        return [
            party for party in parties if party.managers.filter(pk=self.request.user.pk).count() > 0 or party.scanners.filter(pk=self.request.user.pk).count() > 0
        ]

    def get_upcoming_registrations(self):
        return DancingPartyRegistration.objects.filter(
            Q(user=self.request.user)|Q(guarantor=self.request.user),
            dancing_party__event_ends_on__gte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'staffed_parties': self.get_staffed_upcoming_parties(),
            'registrations': self.get_upcoming_registrations()
        })
        return context


class AccountView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_member/lobby/account.html"
    cla_member_active_section = 'account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user': self.request.user,
        })
        return context


class AccountValidationView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_member/lobby/account_validation.html"
    cla_member_active_section = 'account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user': self.request.user,
        })
        return context
