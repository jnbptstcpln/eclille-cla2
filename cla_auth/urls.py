from django.contrib.auth.decorators import login_required
from django.urls import path
from oauth2_provider import views as oauth2_views

from cla_auth import views

app_name = "cla_auth"
urlpatterns = [
    # Session management
    path("connexion", views.session.login, name="login"),
    path("deconnexion", views.session.logout, name="logout"),
    path("oublier", views.session.forgot, name="forgot"),
    path("oublier/identifiant", views.session.forgot_username, name="forgot_username"),
    path("oublier/motdepasse", views.session.forgot_password, name="forgot_password"),
    # Account activation
    path("activation/<str:activation_jwt>", views.activation.activate, name="activate"),
    path(
        "activation/<str:activation_jwt>/rgpd",
        views.activation.activate_rgpd,
        name="activate_rgpd",
    ),
    path(
        "activation/<str:activation_jwt>/motdepasse",
        views.activation.activate_password,
        name="activate_password",
    ),
    # Account validation
    path("validation", views.validation.validate, name="validate"),
    # Changement de mot de passe obligatoire (après un incident de sécurité)
    path("motdepasse/nouveau", views.password_change.password_change_required, name="password_change_required"),
    # Password reset
    path("reinitialiser/<str:reset_jwt>", views.reset.reset, name="reset"),
    # Services
    path(
        "authentification/<str:identifier>",
        views.service.authenticate,
        name="service_authenticate",
    ),
    path(
        "authentification/<str:identifier>/<str:ticket_jwt>",
        views.service.validate,
        name="service_validate",
    ),
    # Docs
    path("__docs/cursus/", views.docs.cursus, name="docs_cursus"),
    # Debugging
    path(
        "__cla_auth/debug/import_legacy_users",
        login_required(views.debug.ImportLegacyUsersView.as_view()),
        name="debug__import_legacy_users",
    ),
]

# OpenID Connect, monté sous /auth/ (cla_web/urls.py) avec le namespace attendu par django-oauth-toolkit.
# Les vues de gestion des applications de django-oauth-toolkit ne sont volontairement pas exposées :
# les applications se créent dans l'administration.
oidc_urlpatterns = (
    [
        path("authorize/", views.oidc.AuthorizationView.as_view(), name="authorize"),
        path("token/", oauth2_views.TokenView.as_view(), name="token"),
        path("revoke_token/", oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
        path("userinfo/", oauth2_views.UserInfoView.as_view(), name="user-info"),
        path("logout/", views.oidc.LogoutView.as_view(), name="rp-initiated-logout"),
        path(".well-known/openid-configuration", oauth2_views.ConnectDiscoveryInfoView.as_view(),
             name="oidc-connect-discovery-info"),
        path(".well-known/jwks.json", oauth2_views.JwksInfoView.as_view(), name="jwks-info"),
    ],
    "oauth2_provider",
)
