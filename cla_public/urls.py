from django.urls import path
from .views import *

app_name = "cla_public"
urlpatterns = [
    path("", IndexPublicView.as_view(), name="index")
]