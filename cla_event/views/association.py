from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import resolve_url, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import UpdateView, CreateView, ListView, View

from cla_association.mixins import AssociationManageMixin
from cla_event.forms import EventAssociationDefaultForm, EventAssociationSentForm, EventCancelForm
from cla_event.mixins import EventAssociationMixin
from cla_event.models import Event


class EventListView(LoginRequiredMixin, AssociationManageMixin, ListView):
    association_manage_active_section = "events"
    template_name = "cla_event/association/list.html"
    model = Event
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(association=self.association)


class EventCreateView(LoginRequiredMixin, AssociationManageMixin, CreateView):
    association_manage_active_section = "events"
    template_name = "cla_event/association/create.html"
    model = Event
    form_class = EventAssociationDefaultForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.association = self.association
        response = super().form_valid(form)
        messages.success(self.request, "L'événement a bien été créé")
        return response

    def get_success_url(self):
        return resolve_url("cla_event:association:update", self.association.slug, self.object.pk)


class EventUpdateView(LoginRequiredMixin, EventAssociationMixin, UpdateView):
    association_manage_active_section = "events"
    template_name = "cla_event/association/update.html"
    model = Event

    def get_form_class(self):
        if self.event.sent:
            return EventAssociationSentForm
        else:
            return EventAssociationDefaultForm

    def get_object(self, queryset=None):
        return self.event

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été sauvegardés")
        return response

    def get_success_url(self):
        return resolve_url("cla_event:association:update", self.association.slug, self.event.pk)


class EventSendView(LoginRequiredMixin, EventAssociationMixin, View):

    def post(self, request, *args, **kwargs):
        if self.event.sent or self.event.validated:
            return redirect("cla_event:association:update", self.association.slug, self.event.pk)

        self.event.sent = True
        self.event.sent_on = timezone.now()
        self.event.save()

        # Only send notification when reservation are validated because
        # event validation required that all associated reservations are validated
        if self.event.are_reservations_validated():
            self.event.send_notification()

        reservations = [
            self.event.get_reservation_barbecue(),
            self.event.get_reservation_bibli(),
            self.event.get_reservation_foyer(),
            self.event.get_reservation_synthe(),
            self.event.get_reservation_dancehall()
        ]
        for r in reservations:
            if r:
                r.sent = True
                r.sent_on = timezone.now()
                r.save()
                r.send_notification()

        messages.success(request, "Votre événement a bien été envoyé !")
        return redirect("cla_event:association:list", self.association.slug)


class EventCancelView(LoginRequiredMixin, EventAssociationMixin, UpdateView):
    association_manage_active_section = "events"
    template_name = "cla_event/association/cancel.html"
    model = Event
    form_class = EventCancelForm

    def dispatch(self, request, *args, **kwargs):
        # Prevent accessing the form if the event is already cancelled
        if self.event.is_cancelled:
            return redirect(self.get_success_url())

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.event

    def form_valid(self, form):
        self.event.cancelled_on = timezone.now()
        self.event.cancelled_by = self.request.user
        self.event.cancelled_hide = form.cleaned_data['cancel_type'] == 'hide'
        self.event.save()
        messages.info(self.request, "Votre événement a bien été annulé" + (" et retiré du calendrier" if self.event.cancelled_hide else ""))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return resolve_url("cla_event:association:update", self.association.slug, self.event.pk)
