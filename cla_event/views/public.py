from django.views.generic import TemplateView

from cla_event.mixins import PlanningMixin
from cla_member.mixins import ClaMemberModuleMixin


class IndexView(PlanningMixin, ClaMemberModuleMixin, TemplateView):
    template_name = "cla_event/public/planning.html"
    cla_member_active_section = "planning"
    config__event_popover = True
    config__event_clickable = False
