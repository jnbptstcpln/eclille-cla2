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

from cla_member.models import Website
from cla_ticketing.models import Event, DancingParty, DancingPartyRegistration


from cla_member.mixins import ClaMemberModuleMixin


class IndexView(ClaMemberModuleMixin, TemplateView):
    template_name = "cla_association/public/index.html"

    def get_associations(self):
        events = Event.objects.filter(
            registration_starts_on__lte=timezone.now(),
            registration_ends_on__gt=timezone.now(),
        )
        return [
            event for event in events if self.request.user.infos.college in event.colleges
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'associations': self.get_associations()
        })
        return context
