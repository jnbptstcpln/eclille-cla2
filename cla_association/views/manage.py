from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse, get_object_or_404, resolve_url
from django.http import HttpRequest, HttpResponseNotAllowed, Http404, HttpResponse
from django.utils import timezone

from cla_association.forms import AssociationForm, AssociationLogoForm, HandoverFolderForm
from cla_association.mixins import AssociationManageMixin
from cla_association.models import Association, HandoverFolder


class IndexView(LoginRequiredMixin, AssociationManageMixin, TemplateView):
    association_manage_active_section = "index"
    template_name = "cla_association/manage/index.html"


class ChangeView(LoginRequiredMixin, AssociationManageMixin, UpdateView):
    association_manage_active_section = "edit"
    template_name = "cla_association/manage/edit.html"
    model = Association
    form_class = AssociationForm

    def get_object(self, queryset=None):
        return self.association

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été sauvegardés")
        return response

    def get_success_url(self):
        return resolve_url("cla_association:manage:change", self.association.slug)


class ChangeLogoView(LoginRequiredMixin, AssociationManageMixin, UpdateView):
    association_manage_active_section = "edit"
    template_name = "cla_association/manage/edit.html"
    model = Association
    form_class = AssociationLogoForm

    def get_object(self, queryset=None):
        return self.association

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Le nouveau logo a bien été sauvegardé")
        return response

    def get_success_url(self):
        return resolve_url("cla_association:manage:change", self.association.slug)


class ManagersView(LoginRequiredMixin, AssociationManageMixin, TemplateView):
    association_manage_active_section = "managers"
    template_name = "cla_association/manage/managers.html"


class HandoverView(LoginRequiredMixin, AssociationManageMixin, TemplateView):
    association_manage_active_section = "handover"
    template_name = "cla_association/manage/handover.html"


class HandoverUploadView(LoginRequiredMixin, AssociationManageMixin, UpdateView):
    association_manage_active_section = "handover"
    template_name = "cla_association/manage/handover_upload.html"
    model = HandoverFolder
    form_class = HandoverFolderForm

    def get_object(self, queryset=None):
        folder = self.association.handover_folder_to_depose
        if folder:
            return folder
        raise Http404()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Le dossier de passation a bien été déposé")
        return response

    def get_success_url(self):
        return resolve_url("cla_association:manage:handover", self.association.slug)