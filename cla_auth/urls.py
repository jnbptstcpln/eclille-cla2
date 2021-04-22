from django.urls import path

from cla_auth import views

app_name = "cla_auth"
urlpatterns = [
    # Session management
    path('connexion', views.session.login, name="login"),
    path('deconnexion', views.session.logout, name="logout"),

    # Account activation
    path('activation/<str:activation_jwt>', views.activation.activate, name="activate"),
    path('activation/<str:activation_jwt>/rgpd', views.activation.activate_rgpd, name="activate_rgpd"),

    # Account validation
    path('validation', views.validation.validate, name="validate"),
]