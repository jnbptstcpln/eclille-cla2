from datetime import datetime

import bleach
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, resolve_url
from django.utils import timezone

from cla_association.mixins import AssociationManageMixin
from cla_event.models import Event
from cla_member.mixins import ClaMemberModuleMixin


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


class EventManageMixin(ClaMemberModuleMixin):
    cla_member_active_section = "planning"
    cla_event_active_section = "index"
    model = None

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm("cla_event.change_event"):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_reservation_item(self):
        return {
            'name': "__RESERVATION_NAME__",
            'icon': "__RESERVATION_ICON__",
            'color': "__RESERVATION_COLOR__",
        }

    def get_sections_navigation(self):
        sections = [
            {
                'id': "index",
                'label': "Événements",
                'href': resolve_url(f"cla_event:manage:index")
            }
        ]
        return sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_active': 'cla_member',
            'sections_navigation': self.get_sections_navigation(),
            'section_active': self.cla_event_active_section,
        })
        return context


class PlanningMixin:
    model = Event
    blocked_slot_model = None

    config__event_clickable = True
    config__event_content = False
    config__event_popover = False
    config__event_non_public_attrs = {
        'backgroundColor': '#fafafa',
        'textColor': '#ccc',
        'borderColor': '#ccc'
    }
    config__event_non_validated_attrs = {
        'backgroundColor': '#eee',
        'textColor': '#888',
        'borderColor': '#888',
    }

    def get_event_content(self, instance: Event):
        return {
            'html': f"[{instance.association.name}]<br>{instance.name}"
        }

    def get_event_class_names(self, instance: Event):
        class_names = []
        if not instance.validated:
            class_names.append('border-dash')
        return class_names

    def get_event_url(self, instance: Event):
        return None

    def get_event_title(self, instance: Event):
        return instance.association.name

    def get_event_popover(self, instance: Event):
        return {
            'popover': True,
            'popover_content': bleach.clean(
                f"""
                <div class='text-center min-width-100'>
                    <div class='font-weight-bold' style='text-lg'>{instance.name}</div>
                    <div class='text-muted text-sm'>{instance.place.name}</span>
                </div>
                """,
                tags=['span', 'br', 'div'],
                attributes={'span': ['class'], 'div': ['class']}
            ),
        }

    def build_event(self, instance: Event):
        e = {
            'title': self.get_event_title(instance),
            'classNames': self.get_event_class_names(instance),
            'start': instance.starts_on.astimezone(timezone.get_current_timezone()),
            'end': instance.ends_on.astimezone(timezone.get_current_timezone()),
        }
        if self.config__event_clickable:
            e['url'] = self.get_event_url(instance)
        if not instance.public and self.config__event_non_public_attrs:
            e.update(self.config__event_non_public_attrs)
        if not instance.validated:
            e.update(self.config__event_non_validated_attrs)
        if self.config__event_content:
            e.update({'eventContent': self.get_event_content(instance)})
        if self.config__event_popover:
            e.update(self.get_event_popover(instance))
        return e

    def get_event_base_queryset(self):
        return self.model.objects.for_member()

    def get_events(self, start, end):
        events = self.get_event_base_queryset().filter(starts_on__gte=start, ends_on__lte=end)
        return [
            self.build_event(e) for e in events
        ]

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('format') == "json":
            start = datetime.strptime(self.request.GET.get('start'), "%Y-%m-%dT%H:%M:%S")
            end = datetime.strptime(self.request.GET.get('end'), "%Y-%m-%dT%H:%M:%S")
            return JsonResponse(
                self.get_events(start, end)
                , safe=False)
        return super().get(request, *args, **kwargs)
