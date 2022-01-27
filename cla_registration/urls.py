from django.urls import path
from .views import user, sharing, imageright, inte

app_name = "cla_registration"
urlpatterns = [
    path("adherer", user.register_introduction, name="register_introduction"),

    # Standalone registration
    path("adherer/pack/centrale", user.CentralePackRegistrationView.as_view(), name="register_pack_centrale"),
    path("adherer/pack/centrale/dd", user.CentralePackDDRegistrationView.as_view(), name="register_pack_centrale_dd"),
    path("adherer/pack/iteem", user.ITEEMPackRegistrationView.as_view(), name="register_pack_iteem"),
    path("adherer/cla/centrale", user.CentraleCLARegistrationView.as_view(), name="register_cla_centrale"),
    path("adherer/cla/centrale/dd", user.CentraleCLADDRegistrationView.as_view(), name="register_cla_centrale_dd"),
    path("adherer/cla/iteem", user.ITEEMCLARegistrationView.as_view(), name="register_cla_iteem"),
    path("adherer/cla/enscl", user.ENSCLCLARegistrationView.as_view(), name="register_cla_enscl"),
    path("adherer/<uuid:pk>", user.RegistrationPaiementView.as_view(), name="register_paiement"),
    path("adherer/<uuid:pk>/cheque", user.RegistrationPaiementCheckView.as_view(), name="register_paiement_check"),

    # Inte registration
    path("inte", inte.IndexView.as_view(), name="inte"),
    path("inte/pack/centrale", inte.PackRegistrationView.as_view(), name="inte_pack_centrale"),
    path("inte/pack/centrale/dd", inte.PackDDRegistrationView.as_view(), name="inte_pack_centrale_dd"),
    path("inte/cla/centrale", inte.CLARegistrationView.as_view(), name="inte_cla_centrale"),
    path("inte/cla/centrale/dd", inte.CLADDRegistrationView.as_view(), name="inte_cla_centrale_dd"),
    path("inte/<uuid:pk>", inte.RegistrationPaiementView.as_view(), name="inte_paiement"),

    path("adhesion/partenaires/<str:session_pk>/<str:sharing_uuid>", sharing.RegistrationsAlumniView.as_view(), name="registration_sharing_alumni"),

    path("droit-image", imageright.CreateAgreementView.as_view(), name="imageright_form"),
    path("droit-image/<uuid:pk>", imageright.SignAgreementView.as_view(), name="imageright_sign")
]
