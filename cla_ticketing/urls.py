from django.urls import path

from cla_ticketing.views import event

app_name = "cla_ticketing"
urlpatterns = [
    path("<str:event_slug>", event.EventRegistrationView.as_view(), name="event_ticketing"),
    path("<str:event_slug>/nonmember", event.EventRegistrationNonMemberView.as_view(), name="event_ticketing_non_member")
]
