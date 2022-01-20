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

from cla_association.models import Association


from cla_member.mixins import ClaMemberModuleMixin


class ListView(TemplateView):
    template_name = "cla_association/public/list.html"

    def get_associations(self):
        return Association.objects.filter(
            display=True
        ).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'associations': self.get_associations(),
            'categories': Association.Category.choices
        })
        return context


class DetailView(TemplateView):
    association: Association = None
    template_name = "cla_association/public/detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.association = get_object_or_404(Association, slug=kwargs.pop("slug"), display=True)
        return super().dispatch(request, *args, **kwargs)

    def get_members(self):
        return self.association.members.filter(user_id__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'association': self.association,
            'members': self.get_members()
        })
        return context
