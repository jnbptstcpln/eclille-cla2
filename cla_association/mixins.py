from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url, redirect, get_object_or_404

from cla_association.models import Association


class AssociationManageMixin:
    association: Association = None
    association_manage_active_section = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.association = get_object_or_404(Association, slug=self.kwargs.pop("slug"))

    def dispatch(self, request, *args, **kwargs):
        if not self.association.active and self.association.members.filter(user=self.request.user).count() == 0:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_sections_navigation(self):
        sections = [
            {
                'id': "index",
                'label': "Accueil",
                'href': resolve_url("cla_association:manage:index", self.association.slug)
            },
            {
                'id': "edit",
                'label': "Modifier",
                'href': resolve_url("cla_association:manage:change", self.association.slug)
            },
            {
                'id': "booking",
                'label': "Réservations",
                'href': resolve_url("cla_member:ticketing")
            },
            {
                'id': "managers",
                'label': "Responsables",
                'href': resolve_url("cla_association:manage:managers", self.association.slug)
            }
        ]
        if self.association.is_club_or_commission:
            sections.append({
                'id': "handover",
                'label': "Passation",
                'href': resolve_url("cla_association:manage:handover", self.association.slug)
            })
        return sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_active': 'cla_member',
            'association': self.association,
            'sections_navigation': self.get_sections_navigation(),
            'section_active': self.association_manage_active_section
        })
        return context
