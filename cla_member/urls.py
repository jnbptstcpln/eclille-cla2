from django.urls import path
from .views import lobby, picture

app_name = "cla_member"
urlpatterns = [
    path("", lobby.IndexView.as_view(), name="lobby"),
    path("billetteries", lobby.TicketingView.as_view(), name="ticketing"),
    path("mon-compte", lobby.AccountView.as_view(), name="account"),
    path("mon-compte/validation", lobby.AccountValidationView.as_view(), name="account_validation"),
    path("mon-compte/justificatif", lobby.MembershipProofView.as_view(), name="membership_proof"),
    path("mes-associations", lobby.AssociationView.as_view(), name="associations"),
    path("email-test", lobby.TestEmailView.as_view(), name="test_email"),

    path("photos", picture.PictureUploadView.as_view(), name="upload_pictures"),
]
