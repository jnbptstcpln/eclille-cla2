from django.contrib import messages
from django.shortcuts import resolve_url, redirect
from django.views.generic import TemplateView, UpdateView, DetailView

from cla_event.forms import EventAdminForm, EventValidateForm, EventRejectForm
from cla_event.mixins import EventManageMixin, PlanningMixin
from cla_event.models import Event


class IndexView(PlanningMixin, EventManageMixin, TemplateView):
    association_manage_active_section = "index"
    template_name = "cla_event/manage/planning.html"

    config__event_popover = True

    def get_event_base_queryset(self):
        return Event.objects.filter(sent=True)

    def get_event_url(self, instance: Event):
        return resolve_url("cla_event:manage:event-detail", instance.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'to_review': Event.objects.filter(sent=True, validated=False, public=True)
        })
        return context


class EventDetailView(PlanningMixin, EventManageMixin, DetailView):
    template_name = "cla_event/manage/event/details.html"
    model = Event

    config__event_clickable = False
    config__event_popover = True

    def get_event_base_queryset(self):
        return Event.objects.filter(public=True, sent=True)

    def build_event(self, instance: Event):
        e = super().build_event(instance)
        if instance.pk == self.get_object().pk:
            e['borderColor'] = "red"
        return e

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_range_free': self.model.objects.is_range_free(self.object.starts_on, self.object.ends_on)
        })
        return context


class EventUpdateView(EventManageMixin, UpdateView):
    template_name = "cla_event/manage/event/update.html"
    model = Event
    form_class = EventAdminForm

    def get_success_url(self):
        return resolve_url("cla_event:manage:event-update", self.object.pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrée")
        return response


class EventValidateView(EventManageMixin, UpdateView):
    template_name = "cla_event/manage/event/validate.html"
    form_class = EventValidateForm
    model = Event

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if not event.are_reservations_validated():
            return redirect("cla_event:manage:event-detail", event.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return resolve_url("cla_event:manage:event-detail", self.object.pk)

    def form_valid(self, form):
        form.instance.validated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "La réservation a bien été validée")
        return response


class EventRejectView(EventManageMixin, UpdateView):
    template_name = "cla_event/manage/event/reject.html"
    form_class = EventRejectForm
    model = Event

    def get_success_url(self):
        return resolve_url("cla_event:manage:event")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance:
            form.instance.reject(form.instance.rejected_for)
        messages.success(self.request, "La réservation a bien été rejetée")
        return response
