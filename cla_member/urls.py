from django.urls import path
from .views.lobby import *

app_name = "cla_member"
urlpatterns = [
    path("", IndexView.as_view(), name="lobby"),
    path("billetteries", TicketingView.as_view(), name="ticketing"),
    path("mon-compte", AccountView.as_view(), name="account"),
    path("mon-compte/validation", AccountValidationView.as_view(), name="account_validation"),
    path("mes-associations", AssociationView.as_view(), name="associations"),
]
