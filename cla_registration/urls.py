from django.urls import path
from .views import *

app_name = "cla_registration"
urlpatterns = [
    path("adherer", register_introduction, name="register_introduction"),
    # Pack
    path("adherer/pack/centrale", CentralePackRegistrationView.as_view(), name="register_pack_centrale"),
    path("adherer/pack/centrale/dd", CentralePackDDRegistrationView.as_view(), name="register_pack_centrale_dd"),
    path("adherer/pack/iteem", ITEEMPackRegistrationView.as_view(), name="register_pack_iteem"),
    # CLA only
    path("adherer/cla/centrale", CentraleCLARegistrationView.as_view(), name="register_cla_centrale"),
    path("adherer/cla/centrale/dd", CentraleCLADDRegistrationView.as_view(), name="register_cla_centrale_dd"),
    path("adherer/cla/iteem", ITEEMCLARegistrationView.as_view(), name="register_cla_iteem"),
    # Success and Paiement
    path("adherer/<uuid:pk>", RegistrationPaiementView.as_view(), name="register_paiement"),
    path("adherer/<uuid:pk>/cheque", RegistrationPaiementCheckView.as_view(), name="register_paiement_check"),
]
