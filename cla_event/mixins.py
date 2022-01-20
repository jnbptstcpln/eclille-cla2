from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from cla_association.mixins import AssociationManageMixin
from cla_event.models import Event


class EventAssociationMixin(AssociationManageMixin):
    association_manage_active_section = "events"
    event: Event = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.event = get_object_or_404(Event, pk=self.kwargs.pop("pk"), association=self.association)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'event': self.event
        })
        return context
