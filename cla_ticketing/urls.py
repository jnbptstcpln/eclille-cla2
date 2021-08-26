from django.urls import path

from cla_ticketing.views import event
from cla_ticketing.views import party

app_name = "cla_ticketing"
urlpatterns = [
    path("<str:event_slug>", event.EventRegistrationView.as_view(), name="event_ticketing"),
    path("<str:event_slug>/nonmember", event.EventRegistrationNonMemberView.as_view(), name="event_ticketing_non_member"),
    path("sd/<str:party_slug>", party.DancingPartyView.as_view(), name="party_view"),
    path("sd/<str:party_slug>/inscription/cotisant", party.ContributorRegistrationCreateView.as_view(), name="party_register_contributor"),
    path("sd/<str:party_slug>/inscription/non-cotisant", party.NonContributorRegistrationCreateView.as_view(), name="party_register_noncontributor"),
    path("sd/<str:party_slug>/cotisant", party.ContributorRegistrationDetailView.as_view(), name="party_detail_contributor"),
    path("sd/<str:party_slug>/non-cotisant", party.NonContributorRegistrationDetailView.as_view(), name="party_detail_noncontributor"),
]
