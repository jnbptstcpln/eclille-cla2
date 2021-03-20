from django.conf import settings
from cla_web.utils import current_school_year


def cla_web_context(request):
    context = {}

    # Project version
    context['project_version'] = settings.PROJECT_VERSION

    # School year
    context['school_year'] = current_school_year()

    return context
