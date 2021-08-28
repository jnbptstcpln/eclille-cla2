from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import resolve_url, redirect


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
                'id': "ticketing",
                'label': "Billetteries",
                'href': resolve_url("cla_member:ticketing")
            },
            {
                'id': "account",
                'label': "Mon compte",
                'href': resolve_url("cla_member:account")
            }
        ]
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