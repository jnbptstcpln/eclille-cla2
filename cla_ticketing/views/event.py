import jwt
import random

from django.views import generic
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponseNotAllowed
from django.utils import timezone

from cla_ticketing.forms import EventRegistrationForm
from cla_ticketing.models import Event, EventRegistration


class EventRegistrationView(generic.CreateView):
    model = EventRegistration
    form_class = EventRegistrationForm
    template_name = "cla_ticketing/event/registration.html"
    event = None
    object = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=kwargs.pop('event_slug'))
        if not request.user.is_authenticated:
            if not self.event.allow_non_contributor_registration:
                return redirect(reverse("cla_auth:login")+f"?next={reverse('cla_ticketing:event_ticketing', self.event.slug)}")
            elif not request.session.get(EventRegistrationNonMemberView.event_non_member_registration_id(self.event), False):
                return render(
                    request,
                    "cla_ticketing/event/registration_login.html",
                    {
                        'event': self.event
                    }
                )
            elif self.request.session.get(self.event_registration_success_id(self.event), False):
                return render(
                    request,
                    "cla_ticketing/event/registration_done.html",
                    {
                        'event': self.event
                    }
                )

        else:
            if EventRegistration.objects.filter(event=self.event, user=self.request.user).count() > 0:
                return render(
                    request,
                    "cla_ticketing/event/registration_done.html",
                    {
                        'event': self.event
                    }
                )
            elif request.user.infos.college not in self.event.colleges:
                return render(
                    request,
                    "cla_ticketing/event/registration_forbidden.html",
                    {
                        'event': self.event
                    }
                )

        if not self.event.are_registrations_opened or self.event.places_remaining <= 0:
            return render(
                request,
                "cla_ticketing/event/registration_closed.html",
                {
                    'event': self.event
                }
            )

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        kwargs['student_status'] = EventRegistration.StudentStatus.NON_CONTRIBUTOR
        if self.request.user.is_authenticated:
            kwargs['student_status'] = EventRegistration.StudentStatus.CONTRIBUTOR
            kwargs['initial'] = {
                "first_name": self.request.user.first_name,
                "last_name": self.request.user.last_name,
                "email": self.request.user.email,
                "phone": self.request.user.infos.phone if hasattr(self.request.user, 'infos') else ""
            }

        return kwargs

    def form_valid(self, form):
        self.object: EventRegistration = form.save(commit=False)
        self.object.event = self.event
        self.object.student_status = EventRegistration.StudentStatus.CONTRIBUTOR if self.request.user.is_authenticated else EventRegistration.StudentStatus.NON_CONTRIBUTOR
        self.object.user = self.request.user if self.request.user.is_authenticated else None
        self.object.created_by = self.request.user if self.request.user.is_authenticated else None
        self.object.save()
        self.request.session[self.event_registration_success_id(self.event)] = True
        return redirect("cla_ticketing:event_ticketing", self.event.slug)

    @staticmethod
    def event_registration_success_id(event):
        return f"event:{event.slug}:event_registration_success_id"


class EventRegistrationNonMemberView(generic.View):

    event = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        print(request.method)
        if request.method == "POST":
            self.event = get_object_or_404(Event, slug=kwargs.pop('event_slug'))

            if request.user.is_authenticated or not self.event.allow_non_contributor_registration:
                return redirect("cla_ticketing:event_ticketing", self.event.slug)

            # Set the non_member_registration_id
            request.session[self.event_non_member_registration_id(self.event)] = True
            return redirect("cla_ticketing:event_ticketing", self.event.slug)

        return HttpResponseNotAllowed(permitted_methods=['post'])

    @staticmethod
    def event_non_member_registration_id(event):
        return f"event:{event.slug}:event_non_member_registration_id"