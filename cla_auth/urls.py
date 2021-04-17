from django.urls import path

from cla_auth import views

app_name = "cla_auth"
urlpatterns = [
    # Session management
    path('connexion', views.session.login, name="login"),
    path('deconnexion', views.session.logout, name="logout"),

    # Account activation
    path('activation/<str:activation_jwt>', views.activation.activate, name="activate"),
]