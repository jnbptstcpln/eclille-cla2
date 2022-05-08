from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, View
from icalendar import Calendar, Event

from cla_event.mixins import PlanningSchoolAdminMixin


class IndexView(PlanningSchoolAdminMixin, TemplateView):
    template_name = "cla_event/school_admin/planning.html"


class IndexIcsView(PlanningSchoolAdminMixin, View):

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        for e in self.get_planning_items(timezone.now() - timedelta(days=15), timezone.now() + timedelta(days=60)):
            event = Event()
            event.add('summary', e['name'])
            event.add('dtstart', e['start'])
            event.add('dtend', e['end'])
            event.add('description', e['name'])
            event.add('location', e['place'])
            cal.add_component(event)

        return HttpResponse(content=cal.to_ical(), content_type='text/calendar')
