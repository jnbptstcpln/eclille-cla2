from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import resolve_url

from cla_association.models import AssociationMember


class ClaMemberModuleMixin(LoginRequiredMixin):
    cla_member_active_section = None

    def get_sections_navigation(self):
        sections = [
            {
                'id': "index",
                'label': "Accueil",
                'href': resolve_url("cla_member:lobby")
            },
            {
                'id': "account",
                'label': "Mon compte",
                'href': resolve_url("cla_member:account")
            },
            {
                'id': "planning",
                'label': "Calendrier",
                'href': resolve_url("cla_event:public:index")
            },
            {
                'id': "reservations",
                'label': "Infrastructures",
                'href': resolve_url("cla_reservation:index")
            },
            {
                'id': "ticketing",
                'label': "Billetteries",
                'href': resolve_url("cla_member:ticketing")
            },
        ]

        if AssociationMember.objects.filter(user=self.request.user, association__active=True).count() > 0:
            sections.append({
                'id': "association",
                'label': "Mes associations",
                'href': resolve_url("cla_member:associations")
            })

        if self.request.user.has_perm("cla_auth.upload_user_picture"):
            sections.append({
                'id': "photos",
                'label': "Photos de profil",
                'href': resolve_url("cla_member:upload_pictures")
            })

        if self.request.user.is_staff:
            sections.append({
                'id': "admin",
                'label': "Administration",
                'href': resolve_url("admin:index")
            })

        return sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_active': 'cla_member',
            'sections_navigation': self.get_sections_navigation(),
            'section_active': self.cla_member_active_section
        })
        return context
