from datetime import timedelta, date, datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from cla_association.mixins import AssociationManageMixin
from cla_event.mixins import EventAssociationMixin
from cla_event.models import Event


class ReservationAssociationMixin(EventAssociationMixin):
    creating = False
    reservation = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.reservation = self.get_reservation()
        if self.reservation is None:
            print(self.model)
            self.creating = True
            self.reservation = self.model(**self.get_reservation_kwargs())

    def dispatch(self, request, *args, **kwargs):
        # If the event was sent or validated directly display a read only view
        # or redirect if no reservation was associated with the event
        if self.event.sent or self.event.validated:
            if self.creating:
                return redirect("cla_event:association:update", self.association.slug, self.event.pk)
            else:
                return render(self.request, self.template_name, self.get_context_data())
        return super().dispatch(request, *args, **kwargs)

    def get_reservation(self):
        return None

    def get_reservation_kwargs(self):
        return {
            'start_date': self.event.start_date,
            'start_time': (datetime.combine(date.today(), self.event.start_time) - timedelta(hours=1, minutes=30)).time(),
            'end_time': (datetime.combine(date.today(), self.event.end_time) + timedelta(hours=1)).time(),
            'multiple_days': self.event.multiple_days
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.reservation})
        return kwargs

    def form_valid(self, form):
        success_message = "Les changements ont bien été enregistrée"
        if self.creating:
            form.instance.created_by = self.request.user
            form.instance.event = self.event
            success_message = "La réservation a bien été créée"

        self.reservation = form.save()

        response = super().form_valid(form)
        messages.success(self.request, success_message)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'reservation': self.reservation
        })
        return context
