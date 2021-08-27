from django.urls import path

from cla_ticketing.views import event
from cla_ticketing.views import party

app_name = "cla_ticketing"
urlpatterns = [

    path("evenements/<str:event_slug>", event.EventRegistrationView.as_view(), name="event_ticketing"),
    path("evenements/<str:event_slug>/nonmember", event.EventRegistrationNonMemberView.as_view(), name="event_ticketing_non_member"),

    path("<str:party_slug>", party.DancingPartyView.as_view(), name="party_view"),
    path("<str:party_slug>/inscription/cotisant", party.ContributorRegistrationCreateView.as_view(), name="party_register_contributor"),
    path("<str:party_slug>/inscription/non-cotisant", party.NonContributorRegistrationCreateView.as_view(), name="party_register_noncontributor"),
    path("<str:party_slug>/cotisant", party.ContributorRegistrationDetailView.as_view(), name="party_detail_contributor"),
    path("<str:party_slug>/non-cotisant", party.NonContributorRegistrationDetailView.as_view(), name="party_detail_noncontributor"),
    path("<str:party_slug>/entree", party.CheckInPartyView.as_view(), name="party_checkin"),
    path("<str:party_slug>/entree/qrcode/<str:token>", party.CheckInQRCodeView.as_view(), name="party_checkin_qrcode"),
    path("<str:party_slug>/entree/pk/<int:registration_pk>", party.CheckInRegistrationView.as_view(), name="party_checkin_registration"),
]
