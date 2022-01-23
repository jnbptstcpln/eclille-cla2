from django.views.generic import TemplateView

from cla_event.mixins import PlanningMixin, PlanningSchoolAdminMixin
from cla_member.mixins import ClaMemberModuleMixin


class IndexView(PlanningSchoolAdminMixin, TemplateView):
    template_name = "cla_event/school_admin/planning.html"
