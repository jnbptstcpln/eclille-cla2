from datetime import timedelta

import bleach
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from icalendar import Calendar, Event as ICalendarEvent

from cla_auth.mixins import JWTMixin
from cla_event.mixins import PlanningMixin
from cla_event.models import Event
from cla_member.mixins import ClaMemberModuleMixin


class IndexView(PlanningMixin, ClaMemberModuleMixin, TemplateView):
    template_name = "cla_event/public/planning.html"
    cla_member_active_section = "planning"
    config__event_popover = True
    config__event_clickable = False

    def can_access_complete_view(self):
        # Event admins can access rich view
        return self.request.user.has_perm('cla_event.change_event')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sync_href': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_event:public:export')}?token={IcsFileView.generate_token()}"
        })
        return context


class IcsFileView(PlanningMixin, JWTMixin, View):

    jwt_payload_key = "cla_event:index:event:v2"

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        for e in self.get_planning_items(timezone.now() - timedelta(days=15), timezone.now() + timedelta(days=60)):
            event = ICalendarEvent()
            event.add('summary', e['name'])
            event.add('dtstart', e['start'])
            event.add('dtend', e['end'])
            event.add('description', e['name'])
            event.add('location', e['place'])
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')
